from django.urls import path
from . import views

urlpatterns = [
    path("add/<int:product_id>/", views.add_cart, name="add_cart"),
    path("remove/<int:product_id>/", views.remove_cart, name="remove_cart"),
    path("data/", views.cart_data, name="cart_data"),
    path("checkout/", views.checkout, name="checkout"),
]