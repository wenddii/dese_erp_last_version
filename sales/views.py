from django.shortcuts import render
from django.db.models import Q

from .models import Sale
from inventory.models import Product, Category


def sales_manager(request):

    search_query = request.GET.get('q', '')

    products = Product.objects.select_related('category').all()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
        )

    sales = (
        Sale.objects
        .select_related('product')
        .order_by('-sale_date')
    )

    # ---------------------
    # CART
    # ---------------------

    cart = request.session.get("cart", {})

    cart_items = []
    cart_total = 0

    for product_id, item in cart.items():

        try:
            product = Product.objects.get(id=product_id)

            qty = item["qty"]

            line_total = qty * float(product.selling_price)

            cart_items.append({
                "product": product,
                "qty": qty,
                "price": product.selling_price,
                "line_total": line_total,
            })

            cart_total += line_total

        except Product.DoesNotExist:
            pass

    context = {
        "products": products,
        "sales": sales,
        "categories": Category.objects.all(),
        "search_query": search_query,

        # Cart
        "cart_items": cart_items,
        "cart_total": cart_total,
        "cart_count": len(cart_items),
    }

    return render(
        request,
        "sales/sales_manager.html",
        context
    )