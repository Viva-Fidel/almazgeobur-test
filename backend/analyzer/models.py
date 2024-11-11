from django.db import models
from django_prometheus.models import ExportModelOperationsMixin


# Create your models here.
class SalesAnalysis(ExportModelOperationsMixin("SalesAnalysis"), models.Model):
    date = models.DateField(help_text="Дата продаж, для которых выполнен анализ")
    analysis_report = models.TextField(
        help_text="Аналитический отчёт, сгенерированный LLM"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Дата и время создания отчёта"
    )

    def __str__(self):
        return f"Отчёт за {self.date}"


class Product(ExportModelOperationsMixin("Product"), models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.PositiveIntegerField(help_text="Ид продута")
    name = models.CharField(max_length=255, help_text="Имя продукта")
    quantity = models.PositiveIntegerField(help_text="Количетсво")
    price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Цена")
    category = models.CharField(max_length=255, help_text="Категория")
    sales_date = models.DateField(help_text="Дата продажи")
    sales_analysis = models.ForeignKey(
        SalesAnalysis, on_delete=models.CASCADE, related_name="products"
    )

    def __str__(self):
        return f"Продукт {self.name}, категория {self.category}"
