from django.shortcuts import redirect
from inventory.models import Product
from sales.models import Sale
from django.db import transaction


def add_cart(request, product_id):

    qty = int(request.POST.get("qty", 1))

    cart = request.session.get("cart", {})

    key = str(product_id)

    if key in cart:
        cart[key]["qty"] += qty

    else:
        cart[key] = {
            "qty": qty
        }

    request.session["cart"] = cart

    return redirect("sales_manager")

def remove_cart(request, product_id):

    cart = request.session.get("cart", {})

    key = str(product_id)

    if key in cart:
        del cart[key]

    request.session["cart"] = cart

    return redirect("sales_manager")

def checkout(request):

    cart = request.session.get("cart", {})

    if not cart:
        return redirect("sales_manager")

    with transaction.atomic():

        for product_id, item in cart.items():

            product = Product.objects.get(id=product_id)

            Sale.objects.create(
                product=product,
                quantity_sold=item["qty"]
            )

        request.session["cart"] = {}

    return redirect("sales_manager")

