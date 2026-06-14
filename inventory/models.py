from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT, 
        related_name="products"
    )
    name = models.CharField(max_length=255,unique=True)
    
    # Financial data for reporting
    # cost_price represents the current acquisition cost per unit
    cost_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00
    )
    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    # Stock tracking
    minimum_stock = models.PositiveIntegerField(default=5)
    current_stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def inventory_asset_value(self):
        """Calculates total value of stock on hand."""
        return self.current_stock * self.cost_price