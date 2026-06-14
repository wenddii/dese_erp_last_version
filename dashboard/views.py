from django.shortcuts import render
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from inventory.models import Product
from sales.models import Sale
from purchases.models import PurchaseBatch
from finance.models import CashFlow
from decimal import Decimal


def dashboard_home(request):

    # -----------------------
    # REVENUE
    # -----------------------
    total_revenue = Sale.objects.aggregate(
        total=Coalesce(
            Sum(F('quantity_sold') * F('selling_price')),
            Decimal('0.00'),
            output_field=DecimalField()
        )
    )['total']

    # -----------------------
    # COGS
    # -----------------------
    cogs = Sale.objects.aggregate(
        total=Coalesce(
            Sum(F('quantity_sold') * F('cost_price_at_sale')),
            Decimal('0.00'),
            output_field=DecimalField()
        )
    )['total']

    # -----------------------
    # GROSS PROFIT
    # -----------------------
    gross_profit = total_revenue - cogs

    # -----------------------
    # INVENTORY VALUE
    # -----------------------
    total_inventory_value = Product.objects.aggregate(
        total=Coalesce(
            Sum(F('current_stock') * F('cost_price')),
            Decimal('0.00'),
            output_field=DecimalField()
        )
    )['total']

    # -----------------------
    # CASH BALANCE
    # -----------------------
    company_balance = CashFlow.get_global_balance()

    context = {
        'company_balance': company_balance,
        'total_revenue': total_revenue,
        'cogs': cogs,
        'gross_profit': gross_profit,
        'total_inventory_value': total_inventory_value,

        'low_stock_items': Product.objects.filter(
            current_stock__lte=F('minimum_stock')
        ),

        'recent_sales': Sale.objects.select_related('product')
            .order_by('-sale_date')[:5],

        'recent_purchases': PurchaseBatch.objects.select_related('product')
            .order_by('-purchase_date')[:5],
    }

    return render(request, 'dashboard/index.html', context)