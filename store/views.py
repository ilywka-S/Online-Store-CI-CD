from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Product, Category, Universe
from .forms import RegisterForm


def home_page(request):
    all_products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'index.html', {'products': all_products, 'categories': categories})


def catalog_page(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    universes = Universe.objects.all()

    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(name__icontains=search_query)

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
        'current_sort': sort_by,
        'search_query': search_query,
    }
    return render(request, 'catalog.html', context)


def account_page(request):
    return render(request, 'account.html')


def product_page(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product.html', {'product': product})


def register_page(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Реєстрацію успішно завершено!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_page(request):
    if request.user.is_authenticated:
        return redirect('account')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('account')
        messages.error(request, "Невірний логін або пароль!")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')