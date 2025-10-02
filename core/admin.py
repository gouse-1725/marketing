from django.contrib import admin
from .models import CustomUser, Product, Prod_category, OTP, Address, Order, OrderItem

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(Prod_category)
admin.site.register(OTP)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(OrderItem)
# You can customize the admin interface further if needed
# For example, by creating custom admin classes.
# Example:
