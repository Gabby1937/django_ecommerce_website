from django.shortcuts import render

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
        
    def add(self, product, quantity=1): # Add product to cart or update its quantity
        product_id = str(product.id)

        if product_id in self.cart:
            self.cart[product_id]['quantity'] += quantity
        else:
            self.cart[product_id] = {'price': str(product.price), 'quantity': quantity}
        
        self.session.modified = True
        
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())
        # return len(self.cart)