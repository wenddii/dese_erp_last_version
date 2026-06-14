from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('categories/add/', views.category_create, name='category_create'),
    path('product/delete/<int:pk>/', views.product_delete, name='product_delete'),
]