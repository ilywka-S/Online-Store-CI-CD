from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Universe

# Create your views here.
def home_page(request):
    all_products = Product.objects.all()

    context = {
        'products': all_products
    }

    return render(request, 'index.html', context)

def catalog_page(request, category_id=None, universe_id=None):
    products = Product.objects.all()
    categories = Category.objects.all()
    universes = Universe.objects.all()

    active_category = None
    active_universe = None

    if category_id:
        active_category = get_object_or_404(Category, id=category_id)
        products = Product.objects.filter(category=active_category)

    elif universe_id:
        active_universe = get_object_or_404(Universe, id=universe_id)
        products = Product.objects.filter(universe=active_universe)
    
    else:
        products = Product.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'universes': universes
    }
    return render(request, 'catalog.html', context)

def account_page(request):
    return render(request, 'account.html')