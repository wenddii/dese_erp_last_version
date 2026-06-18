from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect

from inventory.models import Product
from sales.models import Sale


def _cart_payload(request):

    cart = request.session.get("cart", {})

    cart_items = []
    cart_total = 0

    for product_id, item in cart.items():

        try:

            product = Product.objects.get(id=product_id)

            quantity = item["qty"]
            price = float(product.selling_price)
            line_total = quantity * price

            cart_items.append({
                "product_id": product.id,
                "product_name": product.name,
                "quantity": quantity,
                "price": price,
                "line_total": line_total,
            })

            cart_total += line_total

        except Product.DoesNotExist:

            continue

    return {
        "cart_items": cart_items,
        "cart_total": cart_total,
        "cart_count": len(cart_items),
    }


def add_cart(request, product_id):

    if request.method != "POST":

        return JsonResponse({"success": False, "error": "POST required."}, status=405)

    product = Product.objects.filter(id=product_id).first()

    if not product:

        return JsonResponse({"success": False, "error": "Product not found."}, status=404)

    try:

        qty = int(request.POST.get("qty", 1))

    except (TypeError, ValueError):

        return JsonResponse({"success": False, "error": "Invalid quantity."}, status=400)

    if qty <= 0:

        return JsonResponse({"success": False, "error": "Quantity must be greater than zero."}, status=400)

    cart = request.session.get("cart", {})

    key = str(product_id)

    current_qty = cart.get(key, {}).get("qty", 0)

    new_total_qty = current_qty + qty

    if new_total_qty > product.current_stock:

        return JsonResponse(
            {
                "success": False,
                "error": f"Only {product.current_stock} units of {product.name} are available."
            },
            status=400,
        )

    if key in cart:

        cart[key]["qty"] = new_total_qty

    else:

        cart[key] = {
            "qty": qty
        }

    request.session["cart"] = cart

    payload = _cart_payload(request)

    return JsonResponse({
        "success": True,
        "message": f"{qty} x {product.name} added to cart.",
        **payload,
    })


def remove_cart(request, product_id):

    if request.method != "POST":

        return JsonResponse({"success": False, "error": "POST required."}, status=405)

    cart = request.session.get("cart", {})

    key = str(product_id)

    if key in cart:

        del cart[key]

    request.session["cart"] = cart

    payload = _cart_payload(request)

    return JsonResponse({
        "success": True,
        **payload,
    })


def cart_data(request):

    return JsonResponse({
        "success": True,
        **_cart_payload(request),
    })

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

