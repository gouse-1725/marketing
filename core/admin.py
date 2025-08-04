from django.contrib import admin
from .models import CustomUser, Product, Prod_category

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(Prod_category)
