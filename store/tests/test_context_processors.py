import pytest
from django.test import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from store.context_processors import cart_processor
from store.models import Cart, CartItem, Category, Product


@pytest.fixture
def category(db):
    return Category.objects.create(name="Test")

@pytest.fixture
def product(db, category):
    return Product.objects.create(name="Item", price=20.00, category=category)

@pytest.mark.django_db
class TestCartProcessor:
    def test_anonymous_user_returns_zeroes(self):
        factory = RequestFactory()
        request = factory.get('/')
        request.user = AnonymousUser()
        result = cart_processor(request)
        assert result['cart_items_count'] == 0
        assert result['cart_total_price'] == 0
        assert result['cart'] is None
    
    def test_authenticated_user_returns_cart(self, db):
        user = User.objects.create_user(username="cpuser", password="pass")
        factory = RequestFactory()
        request = factory.get('/')
        request.user = user
        result = cart_processor(request)
        assert result['cart'] is not None
        assert result['cart_items_count'] == 0
    
    def test_cart_processor_reflects_items(self, db, product):
        user = User.objects.create_user(username="cpuser2", password="pass")
        cart = Cart.objects.create(user=user)
        CartItem.objects.create(cart=cart, product=product, quantity=3)
        factory = RequestFactory()
        request = factory.get('/')
        request.user = user
        result = cart_processor(request)
        assert result['cart_items_count'] == 3
        assert result['cart_total_price'] == 60.00