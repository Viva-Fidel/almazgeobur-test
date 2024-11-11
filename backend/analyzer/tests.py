from decimal import Decimal
from xml.etree.ElementTree import Element

import pytest

from .models import Product
from .tasks import (
    extract_data,
    generate_prompt,
    process_sales_data,
    save_analysis_to_db,
    save_products_to_db,
)

# Create your tests here.


@pytest.fixture
def mock_xml_root():
    root = Element("root", {"date": "2024-11-08"})
    products = Element("products")

    product1 = Element("product")

    id_elem = Element("id")
    id_elem.text = "1"
    product1.append(id_elem)

    name_elem = Element("name")
    name_elem.text = "Product A"
    product1.append(name_elem)

    quantity_elem = Element("quantity")
    quantity_elem.text = "100"
    product1.append(quantity_elem)

    price_elem = Element("price")
    price_elem.text = "1500.00"
    product1.append(price_elem)

    category_elem = Element("category")
    category_elem.text = "Electronics"
    product1.append(category_elem)

    products.append(product1)
    root.append(products)
    return root


def test_extract_data(mock_xml_root):
    products_data, total_revenue = extract_data(mock_xml_root)

    assert len(products_data) == 1
    product = products_data[0]
    assert product["product_id"] == "1"
    assert product["name"] == "Product A"
    assert product["quantity"] == 100
    assert product["price"] == Decimal("1500.00")
    assert product["category"] == "Electronics"
    assert product["sales_date"] == "2024-11-08"
    assert total_revenue == Decimal("150000.00")


def test_process_sales_data(mock_xml_root):
    products_data, _ = extract_data(mock_xml_root)
    date, top_products, categories = process_sales_data(products_data, mock_xml_root)

    assert date == "2024-11-08"
    assert len(top_products) == 1
    assert top_products[0]["name"] == "Product A"
    assert categories == {"Electronics"}


def test_generate_prompt():
    total_revenue = Decimal("150000.00")
    top_products = ["Product A"]
    categories = {"Electronics"}
    date = "2024-11-08"

    prompt = generate_prompt(total_revenue, top_products, categories, date)
    expected_prompt = (
        "Проанализируй данные о продажах за 2024-11-08:\n"
        "1. Общая выручка: 150000.00\n"
        "2. Топ-3 товара по продажам: Product A\n"
        "3. Распределение по категориям: Electronics\n\n"
        "Составь краткий аналитический отчет с выводами и рекомендациями."
    )
    assert prompt == expected_prompt


@pytest.mark.django_db
def test_save_analysis_to_db():

    date = "2024-11-08"
    llm_response = "Некоторый ответ от LLM"

    sales_analysis = save_analysis_to_db(date, llm_response)

    assert sales_analysis.pk is not None
    assert sales_analysis.date == date
    assert sales_analysis.analysis_report == llm_response


@pytest.mark.django_db
def test_save_products_to_db():

    date = "2024-11-08"
    llm_response = "Некоторый ответ от LLM"

    sales_analysis = save_analysis_to_db(date, llm_response)

    products_data = [
        {
            "product_id": 1,
            "name": "Product A",
            "quantity": 100,
            "price": 1500.00,
            "category": "Electronics",
            "sales_date": "2024-11-08",
        },
        {
            "product_id": 2,
            "name": "Product B",
            "quantity": 50,
            "price": 500.00,
            "category": "Electronics",
            "sales_date": "2024-11-08",
        },
    ]

    save_products_to_db(products_data, sales_analysis)

    products = Product.objects.filter(sales_analysis=sales_analysis)
    assert products.count() == 2
    assert products[0].sales_analysis == sales_analysis
    assert products[0].product_id == 1
    assert products[1].name == "Product B"
