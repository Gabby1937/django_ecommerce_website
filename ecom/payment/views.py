from django.shortcuts import render
from cart.cart import Cart
from payment.forms import ShippingAddressForm
from payment.models import ShippingAddress

# Create your views here.
def payment_success(request):
    return render(request, 'payment/payment_success.html', {})


def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()
    
    if request.user.is_authenticated:
        # Check out as Logged in User
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        shipping_form = ShippingAddressForm(request.POST or None, instance=shipping_user)
        return render(request, 'payment/checkout.html', {'cart_products': cart_products, 'quantities': quantities, 'totals':totals, 'shipping_form': shipping_form})
    else:
        # Check out as Guest User
        shipping_form = ShippingAddressForm(request.POST or None)
        return render(request, 'payment/checkout.html', {'cart_products': cart_products, 'quantities': quantities, 'totals':totals, 'shipping_form': shipping_form})
