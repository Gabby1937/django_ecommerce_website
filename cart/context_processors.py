from .cart import Cart
from django.conf import settings

# Create context processor so our cart can work on all pages

def cart(request):
    # Return the default data from our cart
    return {'cart': Cart(request)}