import pytest
from django.contrib.auth.models import User
from store.models import Universe, Category, Product, UserProfile, Order, OrderItem, Cart, CartItem

@pytest.mark.django_db
class TestUniverseModel:
    def test_create_universe(self):
        universe = Universe.objects.create(name="Marvel", description="Superheroes")
        assert universe.name == "Marvel"
        assert universe.description == "Superheroes"
        assert str(universe) == "Marvel"

@pytest.mark.django_db
class TestCategoryModel:
    def test_create_category(self):
        category = Category.objects.create(name="Comics", description="Books with pictures")
        assert category.name == "Comics"
        assert category.description == "Books with pictures"
        assert str(category) == "Comics"

@pytest.mark.django_db
class TestProductModel:
    def test_create_product(self):
        category = Category.objects.create(name="Comics")
        universe = Universe.objects.create(name="DC")
        product = Product.objects.create(
            name="Batman Issue 1",
            price=15.99,
            category=category,
            universe=universe,
            manufacturer="DC Comics",
            in_stock=True
        )
        assert product.name == "Batman Issue 1"
        assert product.price == 15.99
        assert product.category == category
        assert product.universe == universe
        assert product.manufacturer == "DC Comics"
        assert product.in_stock is True
        assert str(product) == "Batman Issue 1"

@pytest.mark.django_db
class TestUserProfileModel:
    def test_user_profile_creation_and_properties(self):
        user = User.objects.create_user(username="testuser", password="pass")
        profile = user.userprofile  # сигнал вже створив його
        profile.phone = "123456789"
        profile.address = "Test Ave 1"
        profile.save()

        assert profile.role == "customer"
        assert profile.phone == "123456789"
        assert profile.address == "Test Ave 1"
        assert str(profile) == "testuser (Покупець)"
        assert profile.is_admin() is False
        
    def test_is_admin_true(self):
        user = User.objects.create_user(username="adminuser", password="pass")
        profile = user.userprofile
        profile.role = "admin"
        profile.save()
        assert profile.is_admin() is True

@pytest.mark.django_db
class TestOrderModels:
    def test_order_creation(self):
        user = User.objects.create_user(username="buyer", password="password")
        order = Order.objects.create(user=user, status="new", total_price=100.50)
        assert order.user == user
        assert order.status == "new"
        assert order.total_price == 100.50
        assert str(order) == f"Замовлення #{order.pk}"

    def test_order_item_creation(self):
        user = User.objects.create_user(username="buyer", password="password")
        order = Order.objects.create(user=user)
        category = Category.objects.create(name="Toys")
        product = Product.objects.create(name="Action Figure", price=20.00, category=category)
        
        order_item = OrderItem.objects.create(
            order=order, product=product, quantity=2, price=20.00
        )
        assert order_item.order == order
        assert order_item.product == product
        assert order_item.quantity == 2
        assert order_item.price == 20.00
        assert str(order_item) == f"Action Figure x2"

@pytest.mark.django_db
class TestCartModel:
    def test_cart_str(self):
        user = User.objects.create_user(username="cartuser", password="pass")
        cart = Cart.objects.create(user=user)
        assert str(cart) == "Кошик користувача cartuser"
    
    def test_cart_get_total_price_empty(self):
        user = User.objects.create_user(username="emptyuser", password="pass")
        cart = Cart.objects.create(user=user)
        assert cart.get_total_price() == 0
    
    def test_cart_get_total_price_with_items(self):
        user = User.objects.create_user(username="richuser", password="pass")
        cart = Cart.objects.create(user=user)
        category = Category.objects.create(name="Figures")
        product1 = Product.objects.create(name="Iron Man", price=50.00, category=category)
        product2 = Product.objects.create(name="Thor", price=30.00, category=category)
        CartItem.objects.create(cart=cart, product=product1, quantity=2)
        CartItem.objects.create(cart=cart, product=product2, quantity=1)
        assert cart.get_total_price() == 130
    
    def test_cart_get_total_quantity(self):
        user = User.objects.create_user(username="qtyuser", password="pass")
        cart = Cart.objects.create(user=user)
        category = Category.objects.create(name="Comics")
        product = Product.objects.create(name="Spider-Man", price=10.00, category=category)
        CartItem.objects.create(cart=cart, product=product, quantity=3)
        assert cart.get_total_quantity() == 3

@pytest.mark.django_db
class TestCartItemModel:
    def test_cart_item_str(self):
        user = User.objects.create_user(username="itemuser", password="pass")
        cart = Cart.objects.create(user=user)
        category = Category.objects.create(name="Toys")
        product = Product.objects.create(name="Hulk", price=25.00, category=category)
        item = CartItem.objects.create(cart=cart, product=product, quantity=4)
        assert str(item) == "4 x Hulk"
    
    def test_cart_item_get_total(self):
        user = User.objects.create_user(username="totaluser", password="pass")
        cart = Cart.objects.create(user=user)
        category = Category.objects.create(name="Toys")
        product = Product.objects.create(name="Thor", price=15.00, category=category)
        item = CartItem.objects.create(cart=cart, product=product, quantity=3)
        assert item.get_total() == 45.00