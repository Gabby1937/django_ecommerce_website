from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingAddressForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product
import datetime

# Create your views here.

def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        order = Order.objects.get(id=pk)
        # Get the order items
        items = OrderItem.objects.filter(order=pk)
        
        if request.POST:
            status = request.POST['shipping_status']
            # Check if true or false
            if status == 'true':
                # Get the order
                order = Order.objects.filter(id=pk)
                # Update the status
                now = datetime.datetime.now()
                order.update(shipped=True, date_shipped=now)
            else:
                # Get the order
                order = Order.objects.filter(id=pk)
                # Update the status
                order.update(shipped=False)
            messages.success(request, "Shipping Status Updated")
            return redirect('home')
            
        return render(request, 'payment/orders.html', {"order":order, "items": items})
    
    else:
        messages.success(request, "Access Denied!")
        return redirect('home')

def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            # Grab the order
            order = Order.objects.filter(id=num)
            # Grab Date and Time
            now = datetime.datetime.now()
            # Update Order
            order.update(shipped=True, date_shipped=now)
            # Redirect
            messages.success(request, "Shipping Status Updated")
            return redirect('home')
        return render(request, 'payment/not_shipped_dash.html', {"orders": orders})
    else:
        messages.success(request, "Access Denied!")
        return redirect('home')

def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            # Grab the order
            order = Order.objects.filter(id=num)
            # Grab Date and Time
            now = datetime.datetime.now()
            # Update Order
            order.update(shipped=False, date_shipped=now)
            # Redirect
            messages.success(request, "Shipping Status Updated")
            return redirect('home')
        return render(request, 'payment/shipped_dash.html', {"orders": orders})
    else:
        messages.success(request, "Access Denied!")
        return redirect('home')

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
                        
            # Clear the cart
            cart.clear()
            # Clear shipping session data
            if 'my_shipping' in request.session:
                del request.session['my_shipping']
            request.session.modified = True
                        
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
                        
            # Clear the cart
            cart.clear()
            # Clear shipping session data
            if 'my_shipping' in request.session:
                del request.session['my_shipping']
            request.session.modified = True
                        
                        
            messages.success(request, "Order Placed!")
            return redirect('home')
        
    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def billing_info(request):
    if request.method == 'POST':
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()
        
        shipping_form = ShippingAddressForm(request.POST)
        if shipping_form.is_valid():
            request.session['my_shipping'] = shipping_form.cleaned_data
            billing_form = PaymentForm()
            return render(request, 'payment/billing_info.html', {
                'cart_products': cart_products,
                'quantities': quantities,
                'totals': totals,
                'shipping_info': shipping_form.cleaned_data,
                'billing_form': billing_form
            })
        else:
            messages.error(request, "Invalid shipping information")
            return render(request, 'payment/checkout.html', {
                'cart_products': cart_products,
                'quantities': quantities,
                'totals': totals,
                'shipping_form': shipping_form
            })
    else:
        messages.error(request, "Access denied")
        return redirect('home')


def payment_success(request):
    return render(request, 'payment/payment_success.html', {})


def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()
    
    if request.user.is_authenticated:
        shipping_user, created = ShippingAddress.objects.get_or_create(user=request.user)
        shipping_form = ShippingAddressForm(request.POST or None, instance=shipping_user)
        if request.method == 'POST' and shipping_form.is_valid():
            shipping_form_instance = shipping_form.save(commit=False)
            shipping_form_instance.user = request.user
            shipping_form_instance.save()
            request.session['my_shipping'] = shipping_form.cleaned_data
            return redirect('billing_info')
    else:
        shipping_form = ShippingAddressForm(request.POST or None)
        if request.method == 'POST' and shipping_form.is_valid():
            request.session['my_shipping'] = shipping_form.cleaned_data
            return redirect('billing_info')
        
    return render(request, 'payment/checkout.html', {'cart_products': cart_products, 
                                                     'quantities': quantities, 'totals':totals, 
                                                     'shipping_form': shipping_form})
