from decimal import Decimal
from django.db import models
from inventory.models import Product


class PurchaseBatch(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="purchase_batches"
    )

    batch_number = models.CharField(max_length=100)
    quantity_bought = models.PositiveIntegerField()
    cost_price = models.DecimalField(max_digits=12, decimal_places=2)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)  # ADD THIS
    purchase_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'batch_number'],
                name='unique_product_batch_number'
            )
        ]

    def __str__(self):
        return f"PO Batch {self.batch_number} - {self.product.name}"

    @property
    def total_cost(self):
        return self.quantity_bought * self.cost_price

    def save(self, *args, **kwargs):

        if not self.pk:
            product = self.product

            old_stock = product.current_stock
            old_cost = product.cost_price

            new_stock = old_stock + self.quantity_bought

            if old_stock == 0:
                avg_cost = self.cost_price
            else:
                avg_cost = (
                    (old_stock * old_cost) +
                    (self.quantity_bought * self.cost_price)
                ) / Decimal(new_stock)

            super().save(*args, **kwargs)

            product.current_stock = new_stock
            product.cost_price = avg_cost

            # 🔥 THIS IS WHAT YOU WERE MISSING
            product.selling_price = self.selling_price

            product.save()

        else:
            super().save(*args, **kwargs)

            # optional: allow updates to sync price too
            product = self.product
            product.selling_price = self.selling_price
            product.save(update_fields=["selling_price"])