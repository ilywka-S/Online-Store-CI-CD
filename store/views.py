from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Universe, Cart, CartItem, Order, OrderItem
from .forms import RegisterForm
from django.http import JsonResponse

def home_page(request):
    products = Product.objects.filter(in_stock=True)
    
    cheap_products = products.filter(price__lte=100)
    mid_products = products.filter(price__lte=200)
    
    categories = Category.objects.all()
    
    return render(request, 'index.html', {
        'products': products, 
        'cheap_products': cheap_products, 
        'mid_products': mid_products,     
        'categories': categories
    })


def catalog_page(request):
    products = Product.objects.filter(in_stock=True)
    categories = Category.objects.all()
    universes = Universe.objects.all()

    manufacturers = Product.objects.filter(in_stock=True).exclude(manufacturer='').values_list('manufacturer', flat=True).distinct()

    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(name__icontains=search_query)

    cat_id = request.GET.get('category')
    uni_id = request.GET.get('universe')
    manufacturer_filter = request.GET.get('manufacturer') 
    min_price = request.GET.get('min_price') 
    max_price = request.GET.get('max_price') 
    sort_by = request.GET.get('sort', 'default')

    active_category = int(cat_id) if cat_id and cat_id.isdigit() else None
    active_universe = int(uni_id) if uni_id and uni_id.isdigit() else None

    if active_category:
        products = products.filter(category_id=active_category)
    if active_universe:
        products = products.filter(universe_id=active_universe)
    if manufacturer_filter:
        products = products.filter(manufacturer=manufacturer_filter)
        
    if min_price and min_price.isdigit():
        products = products.filter(price__gte=min_price) 
    if max_price and max_price.isdigit():
        products = products.filter(price__lte=max_price)

    if sort_by == 'price_asc':
        products = products.order_by('price')
    if sort_by == 'price_desc':
        products = products.order_by('-price')

    context = {
        'products': products,
        'categories': categories,
        'universes': universes,
        'manufacturers': manufacturers, 
        'active_category': active_category,
        'active_universe': active_universe,
        'current_manufacturer': manufacturer_filter,
        'current_sort': sort_by,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price, 
    }
    return render(request, 'catalog.html', context)

def product_page(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product.html', {'product': product})


@login_required(login_url='login')
def account_page(request):
    if request.method == 'POST' and 'change_password' in request.POST:
        old_pass = request.POST.get('old_password')
        new_pass = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_password')

        user = request.user

        if not user.check_password(old_pass):
            messages.error(request, "Старий пароль введено неправильно!")
        elif new_pass != confirm_pass:
            messages.error(request, "Нові паролі не збігаються!")
        elif len(new_pass) < 8:
            messages.error(request, "Новий пароль занадто короткий (мінімум 8 символів)!")
        else:
            user.set_password(new_pass)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль успішно змінено!")
            return redirect('account')

    return render(request, 'account.html')

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

@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    quantity = int(request.POST.get('quantity', 1))
    
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not item_created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()
    
    from django.template.loader import render_to_string
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_total_price = cart.get_total_price()
        cart_items_count = cart.get_total_quantity()
        
        cart_html = render_to_string('cart_offcanvas.html', {
            'cart': cart,
            'user': request.user,
            'cart_total_price': cart_total_price,
            'cart_items_count': cart_items_count
        })
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Товар додано в кошик',
            'cart_items_count': cart_items_count,
            'cart_total_price': str(cart_total_price),
            'cart_html': cart_html
        })
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))
    
@login_required(login_url='login')
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required(login_url='login')
def checkout_page(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'checkout.html', {'cart': cart})

@login_required(login_url='login')
def confirm_payment(request):
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)
        
        if cart.items.exists():
            order = Order.objects.create(
                user=request.user,
                total_price=cart.get_total_price()
            )
            
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            
            cart.items.all().delete()
            messages.success(request, "Оплата пройшла успішно! Ваше замовлення збережено в історію.")
            return render(request, 'payment_success.html')
        else:
            messages.error(request, "Ваш кошик порожній.")
            return redirect('home')
            
    return redirect('home')