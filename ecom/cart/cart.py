from django.shortcuts import render
from store.models import Product, Profile
import json

class Cart():
    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)
        self.cart[product_id] = product_qty
        self.session.modified = True

        # Save cart to Profile for authenticated users
        if self.request.user.is_authenticated:
            current_user = Profile.objects.get(user__id=self.request.user.id)
            current_user.old_cart = json.dumps(self.cart)
            current_user.save()

        return self.cart
    
    # def update(self, product, quantity):
    #     product_id = str(product)
    #     product_qty = int(quantity)

    #     ourcart = self.cart
        
    #     ourcart[product_id] = product_qty
        
    #     self.session.modified = True
        
    #     thing = self.cart
    #     return thing
    
    # def __init__(self, request):
    #     self.session = request.session
    #     # Get request
    #     self.request = request
        
    #     # Get the current session key if it exists
    #     cart = self.session.get('session_key')
        
    #     # If the user is new, no session key! Create one
    #     if 'session_key' not in request.session:
    #         cart = self.session['session_key'] = {}
            
    #     # Make sure cart is available on all sessions
    #     self.cart = cart
        
        
    def __init__(self, request):
        self.session = request.session
        self.request = request
        cart = self.session.get('session_key', {})

        # If user is authenticated, merge with old_cart
        if request.user.is_authenticated:
            try:
                current_user = Profile.objects.get(user__id=request.user.id)
                if current_user.old_cart:
                    saved_cart = json.loads(current_user.old_cart)
                    cart.update(saved_cart)  # Merge saved cart with session cart
            except Profile.DoesNotExist:
                pass
            except json.JSONDecodeError:
                current_user.old_cart = ''
                current_user.save()

        if 'session_key' not in request.session:
            cart = self.session['session_key'] = cart

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
        
        # Save cart to Profile for authenticated users
        if self.request.user.is_authenticated:
            current_user = Profile.objects.get(user__id=self.request.user.id)
            current_user.old_cart = json.dumps(self.cart)  # Serialize cart to JSON
            current_user.save()
        
        # # Deal with logged in user
        # if self.request.user.is_authenticated:
        #     current_user = Profile.objects.get(user__id=self.request.user.id)
            
        #     # Convert {'2': 3, '5': 1} to {"2":3,"5":1}
        #     carty = str(self.cart)
        #     carty = carty.replace("\'", "\"")
            
        #     # Save carty to profile model
        #     current_user.update(old_cart=str(carty))
            
        
    # def cart_total(self):
    #     # Get product Ids
    #     product_ids = self.cart.keys()
    #     # Look up those keys in our products database model 
    #     products = Product.objects.filter(id__in=product_ids)
    #     quantities = self.cart
    #     total = 0
    #     for key, val in quantities.items():
    #         # Convert key string to int
    #         key = int(key)
    #         for product in products:
    #             if product.id == key:
    #                 if product.is_sale:
    #                     total += val * (product.sale_price * val)
    #                 else:
    #                     total += val * (product.price * val)
                    
    #     return total
    
    def cart_total(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        quantities = self.cart
        total = 0
        for key, val in quantities.items():
            key = int(key)
            for product in products:
                if product.id == key:
                    if product.is_sale:
                        total += product.sale_price * val
                    else:
                        total += product.price * val
        return total
        
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
    
    def delete(self, product):
        product_id = str(product)
        # Delete from Dictionary/Cart
        if product_id in self.cart:
            del self.cart[product_id]
        self.session.modified = True
            
        # thing = self.cart
        # return thing