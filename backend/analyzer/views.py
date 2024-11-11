from .models import SalesAnalysis, Product
from .serializers import SalesAnalysisSerializer, ProductSerializer
from rest_framework import generics
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='date',
            description='Дата для фильтрации отчетов',
            required=False,
            type=str,
            location=OpenApiParameter.QUERY
        ),
    ]
)
@method_decorator(cache_page(60 * 60 * 2), name='dispatch')
class SalesAnalysisListView(generics.ListAPIView):
    serializer_class = SalesAnalysisSerializer

    def get_queryset(self):
        queryset = SalesAnalysis.objects.all().order_by("-created_at")
        date = self.request.query_params.get('date')
        
        if date is not None:
            queryset = queryset.filter(date=date)
        return queryset
        
@method_decorator(cache_page(60 * 60 * 2), name='dispatch')
class SalesAnalysisDetailView(generics.RetrieveAPIView):
    queryset = SalesAnalysis.objects.all()
    serializer_class = SalesAnalysisSerializer

@extend_schema(
    parameters=[
        OpenApiParameter(
            name='sales_date',
            description='Дата продажи для фильтрации',
            required=False,
            type=str,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name='name',
            description='Название продукта для фильтрации',
            required=False,
            type=str,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name='category',
            description='Категория продукта для фильтрации',
            required=False,
            type=str,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name='min_quantity',
            description='Минимальное количество для фильтрации',
            required=False,
            type=int,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name='max_quantity',
            description='Максимальное количество для фильтрации',
            required=False,
            type=int,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name='min_price',
            description='Минимальная цена для фильтрации',
            required=False,
            type=float,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name='max_price',
            description='Максимальная цена для фильтрации',
            required=False,
            type=float,
            location=OpenApiParameter.QUERY
        ),
    ]
)
@method_decorator(cache_page(60 * 60 * 2), name='dispatch')
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all().order_by("-sales_date")
        
        # Фильтрация по дате продаж 
        sales_date = self.request.query_params.get('sales_date')
        if sales_date is not None:
            queryset = queryset.filter(sales_date=sales_date)

        # Фильтрация по названию продукта
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name__icontains=name)  

        # Фильтрация по категории
        category = self.request.query_params.get('category')
        if category is not None:
            queryset = queryset.filter(category__icontains=category) 

        # Фильтрация по диапазону количества
        min_quantity = self.request.query_params.get('min_quantity')
        if min_quantity is not None:
            queryset = queryset.filter(quantity__gte=min_quantity)  

        max_quantity = self.request.query_params.get('max_quantity')
        if max_quantity is not None:
            queryset = queryset.filter(quantity__lte=max_quantity) 

        # Фильтрация по диапазону цены 
        min_price = self.request.query_params.get('min_price')
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)  

        max_price = self.request.query_params.get('max_price')
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price) 

        return queryset

@method_decorator(cache_page(60 * 60 * 2), name='dispatch')
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
