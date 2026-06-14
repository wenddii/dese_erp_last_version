from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum


class CashFlow(models.Model):

    CATEGORY_CHOICES = [
        ('CAPITAL', 'Business Capital'),
        ('SALE', 'Sales Revenue'),
        ('PURCHASE', 'Inventory Purchase'),
        ('EXPENSE', 'Business Expense'),
    ]

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    description = models.TextField(
        blank=True,
        help_text="Notes about this transaction"
    )

    date = models.DateTimeField(
        auto_now_add=True
    )

    reference_id = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.get_category_display()} - ${self.amount}"

    def clean(self):
        super().clean()

        if self.amount <= 0:
            raise ValidationError(
                "Transaction amount must be greater than zero."
            )

    @property
    def is_income(self):
        return self.category in ['CAPITAL', 'SALE']

    @property
    def is_expense(self):
        return self.category in ['PURCHASE', 'EXPENSE']

    @staticmethod
    def get_global_balance():

        income = CashFlow.objects.filter(
            category__in=['CAPITAL', 'SALE']
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        expenses = CashFlow.objects.filter(
            category__in=['PURCHASE', 'EXPENSE']
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        return income - expenses