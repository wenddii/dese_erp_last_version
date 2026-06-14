from django import forms
from .models import PurchaseBatch

class PurchaseBatchForm(forms.ModelForm):
    class Meta:
        model = PurchaseBatch
        # Form inputs needed to process a warehouse restock run
        fields = ['batch_number', 'product', 'quantity_bought', 'cost_price','selling_price']