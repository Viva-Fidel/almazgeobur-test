from rest_framework import serializers

from .models import Product, SalesAnalysis


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = [
            "id",
            "product_id",
            "name",
            "quantity",
            "price",
            "category",
            "sales_date",
        ]


class SalesAnalysisSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = SalesAnalysis
        fields = ["id", "date", "analysis_report", "created_at", "products"]
