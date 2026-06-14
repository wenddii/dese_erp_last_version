from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from dashboard.views import dashboard_home
from reports.views import reports_home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_home, name='dashboard'),
    path('reports/', reports_home, name='business_reports'),
    path('inventory/', include('inventory.urls')),
    path('sales/', include('sales.urls')),
    path('purchases/', include('purchases.urls')),
    path('finance/', include('finance.urls')),
    path("cart/", include("cart.urls")),
]

# This appends the media directory to your URLs during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)