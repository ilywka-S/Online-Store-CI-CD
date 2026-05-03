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
    path('product/<int:product_id>', views.product_page, name='product'),
    path('register/', views.register_page, name = 'register'),
    path('login/', views.login_page, name = 'login'),
    path('logout/', views.logout_view, name='logout'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_page, name='checkout'),
    path('confirm-payment/', views.confirm_payment, name='confirm_payment'),
    path('account/orders/', views.order_history, name='order_history')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)