from django.shortcuts import render
from store.models import Product

class Cart():
    def __init__(self, request):
        self.session = request.session
        
        # Get the current session key if it exists
        cart = self.session.get('session_key')
        
        # If the user is new, no session key! Create one
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
            
        # Make sure cart is available on all sessions
        self.cart = cart
        
    def add(self, product, quantity): # Add product to cart or update its quantity
        product_id = str(product.id)
        product_qty = str(quantity)

        if product_id in self.cart:
            #self.cart[product_id]['quantity'] += quantity
            pass
        else:
            self.cart[product_id] = int(product_qty)
        
        self.session.modified = True
        
    def __len__(self):
        #return sum(item['quantity'] for item in self.cart.values())
        return len(self.cart)
        
    def get_prods(self):
        # Get ids from cart
        product_ids = self.cart.keys()
        # Use the ids to get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        # return the looked-up products
        return products
    
    def get_quants(self):
        quantities = self.cart
        return quantities
    
    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)
            
        ourcart = self.cart
        
        ourcart[product_id] = product_qty
        
        self.session.modified = True
        
        thing = self.cart
        return thing
    
    def delete(self, product):
        product_id = str(product)
        # Delete from Dictionary/Cart
        if product_id in self.cart:
            del self.cart[product_id]
        self.session.modified = True
            
        # thing = self.cart
        # return thing