from django.urls import path
from . import views

# --- STEP 1 CHECK ---
# Make sure app_name is NOT written here. If 'app_name = "purchases"' is active, 
# Django forces you to write 'purchases:purchase_list' inside base.html.
# For now, keep it global by commenting it out or deleting it:

urlpatterns = [
    path('', views.purchase_list, name='purchase_list'),
    path('restock/', views.purchase_create, name='purchase_create'),
]