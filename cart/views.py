from django.shortcuts import redirect
from inventory.models import Product
from sales.models import Sale
from django.db import transaction
from django.contrib import messages


def add_cart(request, product_id):

    product = Product.objects.get(id=product_id)

    qty = int(request.POST.get("qty", 1))

    if qty <= 0:
        messages.error(request, "Quantity must be greater than zero.")
        return redirect("sales_manager")

    cart = request.session.get("cart", {})

    key = str(product_id)

    current_qty = cart.get(key, {}).get("qty", 0)

    new_total_qty = current_qty + qty

    if new_total_qty > product.current_stock:

        messages.error(
            request,
            f"Only {product.current_stock} units of {product.name} are available."
        )

        return redirect("sales_manager")

    if key in cart:

        cart[key]["qty"] = new_total_qty

    else:

        cart[key] = {
            "qty": qty
        }

    request.session["cart"] = cart

    messages.success(
        request,
        f"{qty} x {product.name} added to cart."
    )

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

