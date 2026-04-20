from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from store import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_page, name = 'home'),
    path('catalog/', views.catalog_page, name = 'catalog'),
    path('account/', views.account_page, name = 'account'),
    path('catalog/category/<int:category_id>', views.catalog_page, name='catalog_by_category'),
    path('catalog/universe/<int:universe_id>', views.catalog_page, name='catalog_by_universe'),
    path('product/<int:product_id>', views.product_page, name='product')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)