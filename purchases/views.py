from django.shortcuts import render, redirect
from django.contrib import messages
from .models import PurchaseBatch
from .forms import PurchaseBatchForm

# 1. READ: View historical restock shipments
def purchase_list(request):
    batches = PurchaseBatch.objects.select_related('product').all().order_by('-purchase_date')
    return render(request, 'purchase/purchase_list.html', {'batches': batches})

# 2. CREATE: Intake a new inventory batch from a vendor
def purchase_create(request):
    if request.method == 'POST':
        form = PurchaseBatchForm(request.POST)
        if form.is_valid():
            # Saving fires your finance signals, increments product stock, and cuts cash pool balance
            batch = form.save()
            
            # Message notification triggers the yellow warnings if account drops below zero
            messages.success(request, f"Batch {batch.batch_number} recorded! Deducted ${batch.quantity_bought * batch.cost_price:.2f} for restocking.")
            return redirect('purchase_list')
    else:
        form = PurchaseBatchForm()
    return render(request, 'purchase/purchase_form.html', {'form': form})