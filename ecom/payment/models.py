from django.db import models
from django.contrib.auth.models import User
from store.models import Product
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import datetime

# Create your models here.
class ShippingAddress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    shipping_full_name = models.CharField(max_length=255, blank=True)
    shipping_email_address = models.CharField(max_length=255, blank=True)
    shipping_address1 = models.CharField(max_length=255, blank=True)
    shipping_address2 = models.CharField(max_length=255, blank=True, null=True)
    shipping_city = models.CharField(max_length=255, blank=True)
    shipping_state = models.CharField(max_length=255, blank=True, null=True)
    shipping_zipcode = models.CharField(max_length=255, blank=True, null=True)
    shipping_country = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = 'Shipping Address'
        verbose_name_plural = 'Shipping Address'
        
    def __str__(self):
        return f'Shipping Address - {str(self.id)}'
    
def create_shipping(sender, instance, created, **kwargs):
    if created:
        user_shipping = ShippingAddress(user=instance)
        user_shipping.save()
        
# Automate the profile thing
post_save.connect(create_shipping, sender=User)

    
#Create order model
class Order(models.Model):
     # Foreign Key to User
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    shipping_address = models.TextField(max_length=15255)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f'Order - {str(self.id)}'
    
    
# Auto add Shipping Date
@receiver(pre_save, sender=Order)
def set_shipping_date_on_update(sender, instance, **kwargs):
    if instance.pk:
        now = datetime.datetime.now()
        obj = sender._default_manager.get(pk=instance.pk)
        if instance.shipped and not obj.shipped:
            instance.date_shipped = now
    
# Create order item model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f'Order Item - {str(self.id)}' 