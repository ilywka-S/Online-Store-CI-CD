from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Universe(models.Model):
    name = models.CharField(max_length = 100, verbose_name = "Назва всесвіту")
    description = models.TextField(blank = True, verbose_name = "Опис")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Всесвіт"
        verbose_name_plural = "Всесвіти"

class Category(models.Model):
    name = models.CharField(max_length = 100, verbose_name = "Назва категорії")
    description = models.TextField(blank = True, verbose_name = "Опис")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Назва товару")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Ціна")
    image = models.ImageField(upload_to='products/', verbose_name="Фото товару")
    Category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категорія")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Товари"