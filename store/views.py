from django.shortcuts import render, redirect
from .models import Product, Category, Customer, Order, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from payment.models import ShippingAddress
from payment.forms import ShippingAddressForm
from django import forms
from django.db.models import Q
from django.conf import settings

def search(request):
    if request.method == "POST":
        searched = request.POST['searched']
        products = Product.objects.filter(Q(name__contains=searched) | Q(description__contains=searched) | Q(category__name__contains=searched))
        return render(request, 'search.html', {'searched': searched, 'products': products})
    else:
        return render(request, 'search.html', {})

# def update_info(request):
#     if request.user.is_authenticated:
#         current_user = Profile.objects.get(user__id=request.user.id)
#         shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
#         shipping_form = ShippingAddressForm(request.POST or None, instance=shipping_user)
#         form = UserInfoForm(request.POST or None, instance=current_user)
        
#         if form.is_valid() or shipping_form.is_valid():
#             form.save()
#             shipping_form.save()
            
#             messages.success(request, ("Your info was updated successfully"))
#             return redirect('home')
#         return render(request, 'update_info.html', {'form': form, 'shipping_form': shipping_form})
    
#     else:
#         messages.success(request, ("You must be logged in to view this page"))
#         return redirect('home')
    
def update_info(request):
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id=request.user.id)
        # Use get_or_create to handle missing or single ShippingAddress
        shipping_user, created = ShippingAddress.objects.get_or_create(user=request.user)
        shipping_form = ShippingAddressForm(request.POST or None, instance=shipping_user)
        form = UserInfoForm(request.POST or None, instance=current_user)
        
        if request.method == 'POST':
            if form.is_valid() and shipping_form.is_valid():
                form.save()
                shipping_form_instance = shipping_form.save(commit=False)
                shipping_form_instance.user = request.user  # Ensure user is set
                shipping_form_instance.save()
                messages.success(request, "Your info was updated successfully")
                return redirect('home')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Profile Info - {field}: {error}")
                for field, errors in shipping_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Shipping Info - {field}: {error}")
        
        return render(request, 'update_info.html', {'form': form, 'shipping_form': shipping_form})
    else:
        messages.error(request, "You must be logged in to view this page")
        return redirect('home')
    
def update_password(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        
        if request.method == "POST":
            form = ChangePasswordForm(current_user, request.POST)
        
            if form.is_valid():
                form.save()
                messages.success(request, ("Your password was updated successfully, Pease re-login"))
                login(request, current_user)  # Re-authenticate the user
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'update_password.html', {'form': form})
    else:
        messages.success(request, ("You must be logged in to view this page"))
        return redirect('home')
    
    
def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)
        
        if user_form.is_valid():
            user_form.save()
            
            login(request, current_user)  # Re-authenticate the user
            messages.success(request, ("Your profile was updated successfully"))
            return redirect('home')
        return render(request, 'update_user.html', {'user_form': user_form})
    
    else:
        messages.success(request, ("You must be logged in to view this page"))
        return redirect('home')
    


def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

def about(request):
    return render(request, 'about.html', {})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ("You have been logged in"))
            return redirect('home')
        else:
            messages.success(request, ("Error logging in - please try again..."))
            return redirect('login')
    else:
        return render(request, 'login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out"))
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Create ShippingAddress for the new user
                ShippingAddress.objects.get_or_create(user=user)
                messages.success(request, "Username created successfully! Please complete your profile info.")
                return redirect('update_info')
            else:
                messages.error(request, "Authentication failed. Please try again.")
        else:
            # Form is invalid, errors will be displayed in the template
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    return render(request, 'register.html', {'form': form})

# def register_user(request):
#     form = SignUpForm()
#     if request.method == "POST":
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password1']
#             user = authenticate(username=username, password=password)
#             login(request, user)
#             ShippingAddress.objects.create(user=user)
#             messages.success(request, ("Username Created - Please complete your profile info"))
#             return redirect('update_info')
#         else:
#             messages.success(request, ("Oops! Something went wrong - please try again..."))
#             return redirect('register')
#     else:
#         return render(request, 'register.html', {'form': form})
    
    
def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product': product})

def category(request, foo):
    # Replace hyphens with spaces to match category names
    foo = foo.replace('-', ' ')
    try:
        # Look up the Category by name
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'category': category, 'products': products})
    except:
        messages.success(request, ("No products found in this category"))
        return redirect('home')
    
def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {'categories': categories})

