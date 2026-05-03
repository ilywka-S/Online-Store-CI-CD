from django.contrib import admin
from .models import Category, Product, Universe, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price']
    list_filter = ['category']
    search_fields = ['name', 'category']
    list_editable = ['price']

@admin.register(Universe)
class UniverseAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name', 'category']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # Не показувати зайві порожні рядки
    readonly_fields = ['price'] # Ціну на момент замовлення краще не міняти випадково

# 2. Налаштовуємо відображення самого Замовлення
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Які колонки показувати в загальному списку замовлень
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    
    # Фільтри збоку (дуже зручно шукати нові замовлення)
    list_filter = ['status', 'created_at']
    
    # Поле пошуку (можна шукати за ID замовлення або нікнеймом юзера)
    search_fields = ['id', 'user__username']
    
    # Додаємо наші товари всередину сторінки замовлення
    inlines = [OrderItemInline]
    
    # Забороняємо змінювати дату створення
    readonly_fields = ['created_at']