from django.urls import path

from . import views

urlpatterns = [
    path('products/', views.products_view, name='products'),
    path('products/<int:product_id>/', views.get_product_by_id, name='get-product-by-id'),
]
