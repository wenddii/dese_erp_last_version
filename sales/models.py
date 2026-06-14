from django.db import models, transaction
from django.core.exceptions import ValidationError
from inventory.models import Product


class Sale(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="sales"
    )

    quantity_sold = models.PositiveIntegerField()

    # selling price at time of sale (snapshot from product)
    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    # cost price snapshot for profit calculation
    cost_price_at_sale = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    sale_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale: {self.quantity_sold}x {self.product.name}"

    def clean(self):
        super().clean()

        if not self.product_id:
            return

        with transaction.atomic():
            fresh_product = Product.objects.select_for_update().get(
                id=self.product_id
            )
            current_db_stock = fresh_product.current_stock

        if self.pk is None:
            if current_db_stock < self.quantity_sold:
                raise ValidationError(
                    f"Not enough stock! Only {current_db_stock} units remain."
                )
        else:
            original = Sale.objects.get(pk=self.pk)
            stock_difference = self.quantity_sold - original.quantity_sold

            if current_db_stock < stock_difference:
                raise ValidationError(
                    f"Cannot update sale. Increasing by {stock_difference} exceeds stock ({current_db_stock})."
                )

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        if is_new:
            # ALWAYS snapshot current product values
            self.cost_price_at_sale = self.product.cost_price
            self.selling_price = self.product.selling_price

        self.full_clean()

        with transaction.atomic():

            if is_new:
                super().save(*args, **kwargs)

                Product.objects.filter(id=self.product_id).update(
                    current_stock=models.F('current_stock') - self.quantity_sold
                )

            else:
                original = Sale.objects.get(pk=self.pk)
                diff = self.quantity_sold - original.quantity_sold

                super().save(*args, **kwargs)

                if diff != 0:
                    Product.objects.filter(id=self.product_id).update(
                        current_stock=models.F('current_stock') - diff
                    )

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            Product.objects.filter(id=self.product_id).update(
                current_stock=models.F('current_stock') + self.quantity_sold
            )
            super().delete(*args, **kwargs)

    @property
    def total_revenue(self):
        return self.quantity_sold * self.selling_price

    @property
    def total_cost(self):
        return self.quantity_sold * self.cost_price_at_sale

    @property
    def profit(self):
        return self.total_revenue - self.total_cost