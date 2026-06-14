from django import forms
from .models import Sale

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        # Ensure these match the exact field names in your Sale model
        # (e.g., product, quantity_sold, sale_price)
        fields = ['product', 'quantity_sold']
        
        # Optional: Add widgets for a better user experience
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity_sold': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }