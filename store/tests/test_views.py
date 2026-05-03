import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Category, Universe, Product, Cart, CartItem


@pytest.fixture
def category(db):
    return Category.objects.create(name="Тестова категорія")

@pytest.fixture
def product(db, category):
    return Product.objects.create(name="Тестовий товар", price=100.0, category=category)

@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="pass123")

@pytest.fixture
def auth_client(client, user):
    client.login(username="testuser", password="pass123")
    return client

# Головна сторінка
@pytest.mark.django_db
class TestHomeView:
    def test_home_status_and_template(self, client, product):
        response = client.get(reverse('home'))
        assert response.status_code == 200
        assert 'index.html' in (t.name for t in response.templates)
    
    def test_home_context_contains_product(self, client, product):
        response = client.get(reverse('home'))
        assert product in response.context['products']
    
    def test_home_only_shows_in_stock(self, client, category):
        out_of_stock = Product.objects.create(name="Out", price=10.0, category=category, in_stock=False)
        in_stock = Product.objects.create(name="In", price=10.0, category=category, in_stock=True)
        response = client.get(reverse('home'))
        assert in_stock in response.context['products']
        assert out_of_stock not in response.context['products']

# Каталог
@pytest.mark.django_db
class TestCatalogView:
    def test_catalog_status(self, client):
        response = client.get(reverse('catalog'))
        assert response.status_code == 200
        assert 'catalog.html' in (t.name for t in response.templates)
    
    def test_catalog_search(self, client, product):
        response = client.get(reverse('catalog') + '?q=Тестовий')
        assert product in response.context['products']
    
    def test_catalog_search_no_results(self, client, product):
        response = client.get(reverse('catalog') + '?q=nonexistent_xyz')
        assert list(response.context['products']) == []
    
    def test_catalog_filter_by_category(self, client, product, category):
        response = client.get(reverse('catalog') + f'?category={category.id}')
        assert product in response.context['products']
    
    def test_catalog_sort_price_asc(self, client, category):
        p1 = Product.objects.create(name="Cheap", price=10.0, category=category)
        p2 = Product.objects.create(name="Expensive", price=500.0, category=category)
        response = client.get(reverse('catalog') + '?sort=price_asc')
        products = list(response.context['products'])
        assert products.index(p1) < products.index(p2)

# Сторінка продукту
@pytest.mark.django_db
class TestProductView:
    def test_product_page_status(self, client, product):
        response = client.get(reverse('product', args=[product.id]))
        assert response.status_code == 200
        assert 'product.html' in (t.name for t in response.templates)
    
    def test_product_page_404(self, client):
        response = client.get(reverse('product', args=[9999]))
        assert response.status_code == 404

# Акаунт
@pytest.mark.django_db
class TestAccountView:
    def test_redirects_unauthenticated(self, client):
        response = client.get(reverse('account'))
        assert response.status_code == 302
        assert '/login/' in response['Location']
    
    def test_authenticated_access(self, auth_client):
        response = auth_client.get(reverse('account'))
        assert response.status_code == 200
        assert 'account.html' in (t.name for t in response.templates)

# Реєстрація
@pytest.mark.django_db
class TestRegisterView:
    def test_register_get(self, client):
        response = client.get(reverse('register'))
        assert response.status_code == 200
        assert 'register.html' in (t.name for t in response.templates)
    
    def test_register_post_valid(self, client):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        response = client.post(reverse('register'), data)
        assert response.status_code == 302
        assert User.objects.filter(username='newuser').exists()
    
    def test_register_post_duplicate_email(self, client, user):
        # user fixture вже має username="testuser", але без email
        # Спочатку реєструємо першого
        client.post(reverse('register'), {
            'username': 'first', 'email': 'dup@example.com',
            'password1': 'StrongPass123!', 'password2': 'StrongPass123!'
        })
        # Тепер пробуємо з тим же email
        response = client.post(reverse('register'), {
            'username': 'second', 'email': 'dup@example.com',
            'password1': 'StrongPass123!', 'password2': 'StrongPass123!'
        })
        assert response.status_code == 200  # форма повертається з помилкою
        assert not User.objects.filter(username='second').exists()

# Логін / Логаут
@pytest.mark.django_db
class TestLoginLogoutView:
    def test_login_get(self, client):
        response = client.get(reverse('login'))
        assert response.status_code == 200
    
    def test_login_valid_credentials(self, client, user):
        response = client.post(reverse('login'), {
            'username': 'testuser', 'password': 'pass123'
        })
        assert response.status_code == 302
        assert response['Location'].endswith(reverse('account'))
    
    def test_login_invalid_credentials(self, client):
        response = client.post(reverse('login'), {
            'username': 'wrong', 'password': 'wrongpass'
        })
        assert response.status_code == 200  # залишається на login сторінці
    
    def test_login_redirect_if_already_authenticated(self, auth_client):
        response = auth_client.get(reverse('login'))
        assert response.status_code == 302
    
    def test_logout(self, auth_client):
        response = auth_client.get(reverse('logout'))
        assert response.status_code == 302
        assert response['Location'] == reverse('home') or '/' in response['Location']