from inventory.models import Product


def get_cart(session):
    return session.get("cart", {})


def add_to_cart(session, product_id, qty=1):
    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id]["qty"] += qty
    else:
        cart[product_id] = {"qty": qty}

    session["cart"] = cart
    session.modified = True


def remove_from_cart(session, product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)

    session["cart"] = cart
    session.modified = True


def clear_cart(session):
    session["cart"] = {}
    session.modified = True


def cart_items(session):
    cart = get_cart(session)

    items = []
    total = 0

    products = Product.objects.filter(id__in=cart.keys())

    for p in products:
        qty = cart[str(p.id)]["qty"]

        line_total = qty * p.selling_price

        items.append({
            "product": p,
            "qty": qty,
            "price": p.selling_price,
            "line_total": line_total
        })

        total += line_total

    return items, total