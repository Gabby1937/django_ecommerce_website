from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingAddressForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product

# Create your views here.

def process_order(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()
        
        
        # Get Billing Info from the last page
        payment_form = PaymentForm(request.POST or None)
        # Get Shipping Session Data
        my_shipping = request.session.get('my_shipping')
        
        # Gather Order Info
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email_address']
        # Create Shipping Address from session Info
        
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        print(shipping_address)
        amount_paid = totals
        
        # Create an Order
        if request.user.is_authenticated:
            # Logged In
            user = request.user
            # Create Order
            create_order = Order(user=user, full_name=full_name,
                                 email=email, shipping_address=shipping_address,
                                 amount_paid=amount_paid)
            create_order.save()
            
            # Get the order ID
            order_id = create_order.pk
            
            # Get product ID
            for product in cart_products:
                product_id = product.id
                
                # Get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price
                    
                # Get quantity
                for key, value in quantities.items():
                    if int(key) == product.id:
                        # create order Item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                        create_order_item.save()
                        
            # Delete our cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    # Delete the key
                    del request.sessions[key]
                        
            messages.success(request, "Order Placed!")
            return redirect('home')
        
        else:
            # Not logged in
            # Create Order
            create_order = Order(full_name=full_name,
                                 email=email, shipping_address=shipping_address,
                                 amount_paid=amount_paid)
            create_order.save()
            
            # Get the order ID
            order_id = create_order.pk
            
            # Get product ID
            for product in cart_products:
                product_id = product.id
                
                # Get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price
                    
                # Get quantity
                for key, value in quantities.items():
                    if int(key) == product.id:
                        # create order Item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
                        create_order_item.save()
                        
            # Delete our cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    # Delete the key
                    del request.sessions[key]
                        
                        
            messages.success(request, "Order Placed!")
            return redirect('home')
        
    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def billing_info(request):
    
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()
        
        # Create a session with Shipping Info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping 
        
        if request.user.is_authenticated:
            # Get The Billing Form
            billing_form = PaymentForm()
            return render(request, 'payment/billing_info.html', {'cart_products': cart_products, 
                                                     'quantities': quantities, 'totals':totals, 
                                                     'shipping_info': request.POST, "billing_form": billing_form})
        else:
            # Get The Billing Form
            billing_form = PaymentForm()
            return render(request, 'payment/billing_info.html', {'cart_products': cart_products, 
                                                     'quantities': quantities, 'totals':totals, 
                                                     'shipping_info': request.POST, "billing_form": billing_form})  
        shipping_form = request.POST       
    else:
        messages.success(request, "Access Denied")
        return redirect('home')


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
