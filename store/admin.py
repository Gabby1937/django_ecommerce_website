from django.contrib import admin
from .models import Category, Customer, Product, Order, Profile
from django.contrib.auth.models import User
# Register your models here.


admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Profile)


# Mix Profile with User
class ProfileInline(admin.StackedInline):
    model = Profile
    # can_delete = False
    # verbose_name_plural = 'Profile'
    
# Extend User Model
class UserAdmin(admin.ModelAdmin):
    model = User
    field = ['username', 'first_name', 'last_name', 'email']
    inlines = [ProfileInline]
    
# Unregister User Model the old way
admin.site.unregister(User)

# Re-register User the new way
admin.site.register(User, UserAdmin)