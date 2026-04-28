from .models import Cart


def cart_processor(request):
    cart_info = {'cart_items_count': 0, 'cart_total_price': 0, 'cart': None}
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_info['cart'] = cart
        cart_info['cart_items_count'] = cart.get_total_quantity()
        cart_info['cart_total_price'] = cart.get_total_price()
    return cart_info