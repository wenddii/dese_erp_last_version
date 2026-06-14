from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Category
from .forms import ProductForm, CategoryForm

def product_list(request):
    products = Product.objects.select_related('category').all()
    categories = Category.objects.all()

    search = request.GET.get("search")
    category = request.GET.get("category")

    if search:
        products = products.filter(name__icontains=search)

    if category:
        products = products.filter(category_id=category)

    return render(request, "inventory/product_list.html", {
        "products": products,
        "categories": categories,
    })

# 2. CREATE: Add a new product
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form, 'action': 'Add New'})

# 4. CREATE: Add a new product category
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully!")
            return redirect('product_create')  # Redirect straight back to adding a product
    else:
        form = CategoryForm()
    return render(request, 'inventory/category_form.html', {'form': form})
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('product_list')
    
    # Optional: Render a confirmation page for GET requests
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})