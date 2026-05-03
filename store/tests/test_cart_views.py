import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Category, Product, Cart, CartItem, Order


@pytest.fixture
def category(db):
    return Category.objects.create(name="Action Figures")

@pytest.fixture
def product(db, category):
    return Product.objects.create(name="Batman", price=50.00, category=category)

@pytest.fixture
def user(db):
    return User.objects.create_user(username="cartuser", password="pass123")

@pytest.fixture
def auth_client(client, user):
    client.login(username="cartuser", password="pass123")
    return client

@pytest.fixture
def cart(db, user):
    return Cart.objects.create(user=user)

# add_to_cart
@pytest.mark.django_db
class TestAddToCartView:
    def test_add_to_cart_unauthenticated_redirects(self, client, product):
        response = client.post(reverse('add_to_cart', args=[product.id]))
        assert response.status_code == 302
        assert '/login/' in response['Location']
    
    def test_add_to_cart_creates_item(self, auth_client, product, user):
        auth_client.post(reverse('add_to_cart', args=[product.id]), {'quantity': 1})
        cart = Cart.objects.get(user=user)
        assert cart.items.filter(product=product).exists()
    
    def test_add_to_cart_increments_quantity(self, auth_client, product, user):
        auth_client.post(reverse('add_to_cart', args=[product.id]), {'quantity': 1})
        auth_client.post(reverse('add_to_cart', args=[product.id]), {'quantity': 2})
        cart = Cart.objects.get(user=user)
        item = cart.items.get(product=product)
        assert item.quantity == 3
    
    def test_add_to_cart_ajax_returns_json(self, auth_client, product):
        response = auth_client.post(
            reverse('add_to_cart', args=[product.id]),
            {'quantity': 1},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'cart_items_count' in data
        assert 'cart_total_price' in data
        assert 'cart_html' in data
    
    def test_add_to_cart_nonexistent_product(self, auth_client):
        response = auth_client.post(reverse('add_to_cart', args=[9999]))
        assert response.status_code == 404

# remove_from_cart
@pytest.mark.django_db
class TestRemoveFromCartView:
    def test_remove_from_cart_unauthenticated(self, client, cart, product):
        item = CartItem.objects.create(cart=cart, product=product, quantity=1)
        response = client.post(reverse('remove_from_cart', args=[item.id]))
        assert response.status_code == 302
        assert '/login/' in response['Location']
    
    def test_remove_from_cart_success(self, auth_client, cart, product, user):
        item = CartItem.objects.create(cart=cart, product=product, quantity=1)
        auth_client.post(reverse('remove_from_cart', args=[item.id]))
        assert not CartItem.objects.filter(id=item.id).exists()
    
    def test_cannot_remove_other_users_item(self, client, product, db):
        # Інший юзер з іншим кошиком
        other_user = User.objects.create_user(username="other", password="pass123")
        other_cart = Cart.objects.create(user=other_user)
        item = CartItem.objects.create(cart=other_cart, product=product, quantity=1)
        # Авторизуємось як третій юзер
        attacker = User.objects.create_user(username="attacker", password="pass123")
        client.login(username="attacker", password="pass123")
        response = client.post(reverse('remove_from_cart', args=[item.id]))
        assert response.status_code == 404  # get_object_or_404 захищає

# checkout_page
@pytest.mark.django_db
class TestCheckoutView:
    def test_checkout_unauthenticated(self, client):
        response = client.get(reverse('checkout'))
        assert response.status_code == 302
        assert '/login/' in response['Location']
    
    def test_checkout_authenticated(self, auth_client):
        response = auth_client.get(reverse('checkout'))
        assert response.status_code == 200
        assert 'checkout.html' in (t.name for t in response.templates)
    
    def test_checkout_context_has_cart(self, auth_client, user):
        response = auth_client.get(reverse('checkout'))
        assert 'cart' in response.context

# confirm_payment
@pytest.mark.django_db
class TestConfirmPaymentView:
    def test_confirm_payment_unauthenticated(self, client):
        response = client.post(reverse('confirm_payment'))
        assert response.status_code == 302
        assert '/login/' in response['Location']
    
    def test_confirm_payment_with_items_creates_order(self, auth_client, cart, product, user):
        CartItem.objects.create(cart=cart, product=product, quantity=2)
        response = auth_client.post(reverse('confirm_payment'))
        assert response.status_code == 200
        assert Order.objects.filter(user=user).exists()
    
    def test_confirm_payment_clears_cart(self, auth_client, cart, product, user):
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        auth_client.post(reverse('confirm_payment'))
        cart.refresh_from_db()
        assert cart.items.count() == 0
    
    def test_confirm_payment_empty_cart_redirects(self, auth_client, cart, user):
        # кошик порожній — має редіректити на home
        response = auth_client.post(reverse('confirm_payment'))
        assert response.status_code == 302
    
    def test_confirm_payment_get_redirects(self, auth_client):
        response = auth_client.get(reverse('confirm_payment'))
        assert response.status_code == 302

# order_history
@pytest.mark.django_db
class TestOrderHistoryView:
    def test_order_history_unauthenticated(self, client):
        response = client.get(reverse('order_history'))
        assert response.status_code == 302
        assert '/login/' in response['Location']
    
    def test_order_history_authenticated_empty(self, auth_client):
        response = auth_client.get(reverse('order_history'))
        assert response.status_code == 200
        assert 'order_history.html' in (t.name for t in response.templates)
    
    def test_order_history_shows_user_orders(self, auth_client, user):
        order = Order.objects.create(user=user, total_price=100)
        response = auth_client.get(reverse('order_history'))
        assert order in response.context['orders']