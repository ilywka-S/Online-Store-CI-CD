from django.shortcuts import render
from .models import Product, Category

# Create your views here.
def home_page(request):
    all_products = Product.objects.all()

    context = {
        'products': all_products
    }

    return render(request, 'index.html', context)

def catalog_page(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories
    }
    return render(request, 'catalog.html', context)

def account_page(request):
    return render(request, 'account.html')