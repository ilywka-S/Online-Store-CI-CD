from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Universe

# Create your views here.
def home_page(request):
    all_products = Product.objects.all()
    categories = Category.objects.all()

    context = {
        'products': all_products,
        'categories': categories
    }

    return render(request, 'index.html', context)

def catalog_page(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    universes = Universe.objects.all()

    cat_id = request.GET.get('category')
    uni_id = request.GET.get('universe')
    sort_by = request.GET.get('sort', 'default')

    active_category = int(cat_id) if cat_id and cat_id.isdigit() else None
    active_universe = int(uni_id) if uni_id and uni_id.isdigit() else None

    if active_category:
        products = products.filter(category_id=active_category)

    if active_universe:
        products = products.filter(universe_id=active_universe)

    if sort_by == 'price_asc':
        products = products.order_by('price')
    if sort_by == 'price_desc':
        products = products.order_by('-price')

    context = {
        'products': products,
        'categories': categories,
        'universes': universes,
        'active_category': active_category,
        'active_universe': active_universe,
        'current_sort': sort_by
    }   
    return render(request, 'catalog.html', context)

def account_page(request):
    return render(request, 'account.html')

def product_page(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(request, 'product.html', {'product': product})