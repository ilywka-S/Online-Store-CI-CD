from django.shortcuts import render
from .models import Product

# Create your views here.
def home_page(request):
    all_products = Product.objects.all()

    context = {
        'products': all_products
    }

    return render(request, 'index.html', context)

def catalog_page(request):
    return render(request, 'catalog.html')

def account_page(request):
    return render(request, 'account.html')