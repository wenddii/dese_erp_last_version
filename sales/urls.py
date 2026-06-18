from django.urls import path
from . import views

urlpatterns = [
    # This single URL covers both recording and viewing
    path('', views.sales_manager, name='sales_manager'),
    
]