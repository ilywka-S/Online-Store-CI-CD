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
    name = models.CharField(max_length = 200, verbose_name = "Назва товару")
    description = models.TextField(blank = True, verbose_name = "Опис товару")
    price = models.DecimalField(max_digits = 8, decimal_places = 2, verbose_name = "Ціна")
    image = models.ImageField(upload_to = "products/", blank = True, verbose_name = "Фото товару")
    category = models.ForeignKey(Category, on_delete = models.CASCADE, verbose_name = "Категорія")
    universe = models.ForeignKey(Universe, on_delete = models.SET_NULL, null = True, blank = True, verbose_name = "Всесвіт")
    manufacturer = models.CharField(max_length = 100, blank = True, verbose_name = "Виробник")
    in_stock = models.BooleanField(default = True, verbose_name = "В наявності")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('customer', 'Покупець'),
        ('admin', 'Адміністратор')
    ]

    user = models.OneToOneField(User, on_delete = models.CASCADE, verbose_name = "Користувач")
    role = models.CharField(max_length = 20, choices = ROLE_CHOICES, default = 'customer', verbose_name = "Роль")
    phone = models.CharField(max_length = 20, blank = True, verbose_name = "Номер телефону")
    address = models.TextField(blank = True, verbose_name = "Адреса доставки")

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    def is_admin(self):
        return self.role == 'admin'

    class Meta:
        verbose_name = "Профіль користувача"
        verbose_name_plural = "Профілі користувачів"

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Нове'),
        ('processing', 'В обробці'),
        ('shipped', 'Відправлено'),
        ('delivered', 'Доставлено'),
        ('cancelled', 'Скасовано'),
    ]

    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = "Користувач")
    created_at = models.DateTimeField(auto_now_add = True, verbose_name = "Дата створення")
    status = models.CharField(max_length = 20, choices = STATUS_CHOICES, default = 'new', verbose_name = "Статус")
    total_price = models.DecimalField(max_digits = 10, decimal_places = 2, default = 0, verbose_name = "Сума замовлення")

    def __str__(self):
        return f"Замовлення #{self.pk}"

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete = models.CASCADE, related_name = 'items', verbose_name = "Замовлення")
    product = models.ForeignKey(Product, on_delete = models.CASCADE, verbose_name = "Товар")
    quantity = models.PositiveIntegerField(default = 1, verbose_name = "Кількість")
    price = models.DecimalField(max_digits = 8, decimal_places = 2, verbose_name = "Ціна на момент замовлення")

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    class Meta:
        verbose_name = "Позиція замовлення"
        verbose_name_plural = "Позиції замовлення"
        
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name="Користувач")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    def __str__(self):
        return f"Кошик користувача {self.user.username}"
    def get_total_price(self):
        return sum(item.get_total() for item in self.items.all())
    def get_total_quantity(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE, verbose_name="Кошик")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Кількість")
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    def get_total(self):
        return self.product.price * self.quantity
    
    