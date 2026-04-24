import pytest
from django.contrib.auth.models import User
from store.models import Universe, Category, Product, UserProfile, Order, OrderItem

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
