from datetime import datetime
from decimal import Decimal
import logging
import os
import requests
from celery import shared_task
import xml.etree.ElementTree as ET
from django.db import transaction
from openai import OpenAI

from dotenv import load_dotenv

from .models import Product, SalesAnalysis

load_dotenv()

logger = logging.getLogger(__name__)

def fetch_xml(url):
    """Получение XML файла по запросу"""

    response = requests.get(url)
    response.raise_for_status()  
    root = ET.fromstring(response.content)
    return root

def extract_data(root):
    """Извлечение данных из XML и сохранение их в списке"""
    
    products_data = []
    total_revenue = 0

    sales_date = root.attrib['date']

    for product in root.find('products').findall('product'):
        quantity = int(product.find('quantity').text)
        price = Decimal(product.find('price').text)
        revenue = quantity * price
        total_revenue += revenue

        product_data = {
            'product_id': product.find('id').text,
            'name': product.find('name').text,
            'quantity': quantity,
            'price': price,
            'category': product.find('category').text,
            'sales_date': sales_date,
        }
        products_data.append(product_data)
    return products_data, total_revenue

def process_sales_data(products_data, root):
    """Обрабатывает данные о продажах: извлекает дату, топовые товары и категории."""
    # Извлечение даты
    date = root.attrib['date']
    
    # Определение топ-3 продуктов по количеству
    top_products = sorted(products_data, key=lambda x: x['quantity'], reverse=True)[:3]
    
    # Извлечение уникальных категорий
    categories = {product['category'] for product in products_data}
    
    return date, top_products, categories

def save_analysis_to_db(date, llm_response):
    """Сохранение данных о анализе продаж в БД и возврат созданного экземпляра"""
    sales_analysis = SalesAnalysis(
        date=date,
        analysis_report=llm_response
    )
    sales_analysis.save()
    return sales_analysis

def save_products_to_db(products_data, sales_analysis):
    """Сохранение данных о продуктах в БД с использованием bulk_create и привязкой к анализу"""
    products = [
        Product(sales_analysis=sales_analysis, **product_data) for product_data in products_data
    ]
    Product.objects.bulk_create(products)

def generate_prompt(total_revenue, top_products, categories, date):
    """Создание промпта для LLM"""

    print(top_products)
    print(categories)

    top_products_text = ", ".join([f"{product['name']} {product['quantity']} шт." for product in top_products])
    categories_text = ", ".join(categories)
    prompt = (
        f"Проанализируй данные о продажах за {date}:\n"
        f"1. Общая выручка: {total_revenue}\n"
        f"2. Топ-3 товара по продажам: {top_products_text}\n"
        f"3. Распределение по категориям: {categories_text}\n\n"
        "Составь краткий аналитический отчет с выводами и рекомендациями."
    )
    return prompt

def fetch_llm(prompt):
    """Запрос к LLM и получение ответа"""
    
    api_key = os.getenv("API_KEY")
    model = os.getenv("MODEL")

    client = OpenAI(
    api_key=api_key,
)
    chat_response = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    model=model,
)
    return chat_response.choices[0].message['content']

@shared_task(bind=True, max_retries=3, default_retry_delay=2)
def fetch_and_analyze_sales_data(self, url):
    try:
        logger.info(f"Старт получения данных из XML по ссылке: {url}")

        # 1. Парсинг XML
        root = fetch_xml(url)
        logger.info(f"Данные получены из XML корректно: {url}")

        # 2. Извлечение данных о продуктах из XML
        products_data, total_revenue = extract_data(root)
        logger.info(f"Данные о продуктах извлечены корректно")

        # 3. Формирование данных для анализа
        date, top_products, categories = process_sales_data(products_data, root)
        logger.info(f"Данные для анализа сформированы корректно")

        # 4. Формирование промпта для LLM
        prompt = generate_prompt(total_revenue, top_products, categories, date)
        logger.info(f"Промт запрос создан корректно: {prompt}")

        # 5. Запрос к LLM через API 
        llm_response = fetch_llm(prompt)
        print(f"Был получен ответ от LLM: {llm_response}")

        # 6. Сохранение данных в БД
        with transaction.atomic():
            # Сохранение анализа продаж и получение экземпляра
            sales_analysis = save_analysis_to_db(date, llm_response)
            logger.info(f"Ответ LLM сохранен в БД корректно")

            # Сохранение данных о продуктах и привязка к анализу
            save_products_to_db(products_data, sales_analysis)
            logger.info(f"Данные о продуктах сохранены в БД корректно")
        
        logger.info("Процесс завершен успешно")
        return 'Данные о продажах успешно получены, проанализированы и сохранены'

    except requests.RequestException as e:
        error_msg = f"Ошибка при получении XML файла: {str(e)}"
        logger.error(error_msg)
        self.retry(exc=e)
    except ET.ParseError as e:
        error_msg = f"Ошибка при разборе XML файла: {str(e)}"
        logger.error(error_msg)
        self.retry(exc=e)
    except Exception as e:
        error_msg = f"Произошла ошибка: {str(e)}"
        logger.error(error_msg)
        return f'Произошла ошибка: {str(e)}'