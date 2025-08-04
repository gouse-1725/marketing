from django.urls import path
from . import views

urlpatterns = [
    path('', views.products, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('products/', views.products, name='products'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('contact/', views.contact, name='contact'),
    path('business-plan/', views.business_plan, name='business_plan'),
    path('about/', views.about, name='about'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart, name='cart'),
    path('payment/', views.payment, name='payment'),
    path('checkout/', views.checkout, name='checkout'),
    path('recent-purchases/', views.recent_purchases, name='recent_purchases'),
]