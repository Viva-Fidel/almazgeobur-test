from django.urls import path

from .views import SalesAnalysisListView, SalesAnalysisDetailView, ProductListView, ProductDetailView

urlpatterns = [
    path('sales_analyses/', SalesAnalysisListView.as_view(), name='sales-analysis-list'),
    path('sales_analyses/<int:pk>/', SalesAnalysisDetailView.as_view(), name='sales-analysis-detail'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]