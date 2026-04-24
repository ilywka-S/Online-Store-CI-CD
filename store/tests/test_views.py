import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from store.models import Category, Universe, Product, User

@pytest.mark.django_db
class TestViews:
    def test_home_page_view(self, client):
        # Додамо тестові дані для перевірки їх наявності в контексті
        category = Category.objects.create(name="Тестова категорія")
        dummy_image = SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        product = Product.objects.create(name="Тестовий товар", price=100.0, category=category, image=dummy_image)
        
        url = reverse('home')
        response = client.get(url)
        
        assert response.status_code == 200
        # Перевіряємо що використано правильний шаблон
        assert 'index.html' in (t.name for t in response.templates)
        # Перевіряємо що товари передаються до контексту
        assert 'products' in response.context
        assert list(response.context['products']) == [product]

    def test_catalog_page_view(self, client):
        url = reverse('catalog')
        response = client.get(url)
        assert response.status_code == 200
        assert 'catalog.html' in (t.name for t in response.templates)

    def test_account_page_redirects_unauthenticated(self, client):
        response = client.get(reverse('account'))
        assert response.status_code == 302
        assert '/login/' in response['Location']

    def test_account_page_authenticated(self, client):
        User.objects.create_user(username='testuser', password='pass123')
        client.login(username='testuser', password='pass123')
        response = client.get(reverse('account'))
        assert response.status_code == 200
        assert 'account.html' in (t.name for t in response.templates)
