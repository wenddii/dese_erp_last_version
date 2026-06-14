from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from sales.models import Sale
from purchases.models import PurchaseBatch
from .models import CashFlow


# -------------------------
# SALES → CASH IN
# -------------------------
@receiver(post_save, sender=Sale)
def record_sale_cash_flow(sender, instance, created, **kwargs):

    total_revenue = instance.quantity_sold * instance.selling_price

    if created:
        CashFlow.objects.create(
            category='SALE',
            amount=total_revenue,
            description=f"Sale: {instance.quantity_sold}x {instance.product.name}",
            reference_id=instance.id
        )
    else:
        cf = CashFlow.objects.filter(
            category='SALE',
            reference_id=instance.id
        ).first()

        if cf:
            cf.amount = total_revenue
            cf.save()


@receiver(post_delete, sender=Sale)
def remove_sale_cash_flow(sender, instance, **kwargs):

    CashFlow.objects.filter(
        category='SALE',
        reference_id=instance.id
    ).delete()


# -------------------------
# PURCHASES → CASH OUT
# -------------------------
@receiver(post_save, sender=PurchaseBatch)
def record_purchase_cash_flow(sender, instance, created, **kwargs):

    total_cost = instance.quantity_bought * instance.cost_price

    if created:
        CashFlow.objects.create(
            category='PURCHASE',
            amount=total_cost,
            description=f"Purchase Batch {instance.batch_number}",
            reference_id=instance.id
        )
    else:
        cf = CashFlow.objects.filter(
            category='PURCHASE',
            reference_id=instance.id
        ).first()

        if cf:
            cf.amount = total_cost
            cf.save()


@receiver(post_delete, sender=PurchaseBatch)
def remove_purchase_cash_flow(sender, instance, **kwargs):

    CashFlow.objects.filter(
        category='PURCHASE',
        reference_id=instance.id
    ).delete()