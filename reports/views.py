from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, F, DecimalField, ExpressionWrapper, Q
from django.db.models.functions import TruncDay, Coalesce
from datetime import timedelta, datetime  # Added datetime for manual string parsing
from decimal import Decimal
from finance.models import CashFlow
from sales.models import Sale

def reports_home(request):
    now = timezone.now()
    
    # 1. Capture query inputs from the request context
    days_filter = request.GET.get('days')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # 2. Determine final start and end dates for database query execution
    start_date = None
    end_date = None

    if start_date_str and end_date_str:
        try:
            # Parse custom user strings ("YYYY-MM-DD") into timezone-aware datetimes
            parsed_start = datetime.strptime(start_date_str, "%Y-%m-%d")
            parsed_end = datetime.strptime(end_date_str, "%Y-%m-%d")
            
            # Make dates span the full operational day (00:00:00 to 23:59:59)
            start_date = timezone.make_aware(datetime.combine(parsed_start, datetime.min.time()))
            end_date = timezone.make_aware(datetime.combine(parsed_end, datetime.max.time()))
            
            days_count = (parsed_end - parsed_start).days
        except ValueError:
            # Fallback to defaults if custom input strings are invalid
            days_count = 30
            start_date = now - timedelta(days=days_count)
            end_date = now
    else:
        # Fallback to standard timeframe filter logic if custom fields are empty
        try:
            days_count = int(days_filter) if days_filter else 30
        except ValueError:
            days_count = 30
        start_date = now - timedelta(days=days_count)
        end_date = now

    # --- 1. PERIOD REVENUE & EXPENSES ---
    # Filter using a range constraint matching both start and end parameters
    period_flows = CashFlow.objects.filter(date__range=(start_date, end_date))
    
    period_revenue = period_flows.filter(category='SALE').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    period_expenses = period_flows.filter(category='PURCHASE').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    period_profit = period_revenue - period_expenses

    # --- 2. DAILY BREAKDOWN (TIMELINE TRENDS) ---
    daily_report = (
        CashFlow.objects.filter(date__range=(start_date, end_date))
        .annotate(day=TruncDay('date'))
        .values('day')
        .annotate(
            revenue=Coalesce(Sum('amount', filter=Q(category='SALE')), Decimal('0.00')),
            expense=Coalesce(Sum('amount', filter=Q(category='PURCHASE')), Decimal('0.00'))
        )
        .annotate(
            net_earnings=ExpressionWrapper(F('revenue') - F('expense'), output_field=DecimalField())
        )
        .order_by('-day')
    )

    # --- 3. PROFIT PER PRODUCT PERFORMANCE ---
    # Filtering sales records inside the matching historical time scope
    product_performance = (
        Sale.objects.filter(sale_date__range=(start_date, end_date))
        .values('product__name')
        .annotate(
            units_sold=Sum('quantity_sold'),
            total_revenue=Sum(F('quantity_sold') * F('selling_price'), output_field=DecimalField())
        )
        .order_by('-total_revenue')
    )

    context = {
        'days_count': days_count,
        'period_revenue': period_revenue,
        'period_expenses': period_expenses,
        'period_profit': period_profit,
        'daily_report': daily_report,
        'product_performance': product_performance,
        'start_date_val': start_date_str or '',
        'end_date_val': end_date_str or '',
    }
    
    return render(request, 'reports/analytics.html', context)