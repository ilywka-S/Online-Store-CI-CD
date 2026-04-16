from django.contrib import admin
from .models import Category, Product, Universe

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