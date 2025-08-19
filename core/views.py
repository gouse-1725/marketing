# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.contrib.auth.forms import AuthenticationForm
# from django.core.mail import send_mail
# from django.conf import settings
# from django.utils import timezone
# import logging
# import random
# import string
# import qrcode
# import os
# import sys
# from PIL import Image
# from .forms import CustomUserCreationForm, ContactForm, ForgotPasswordForm, OTPForm, ResetPasswordForm
# from .models import CustomUser, Product, Prod_category, OTP, Order, OrderItem
# from .utils import send_sms

# logger = logging.getLogger(__name__)

# def get_cart(request):
#     """Retrieve or initialize cart from session."""
#     cart = request.session.get('cart', {}) if request.user.is_authenticated else {}
#     cart_items = []
#     cart_total = 0
#     for product_id, quantity in cart.items():
#         try:
#             product = get_object_or_404(Product, id=product_id)
#             item_total = product.price * quantity
#             cart_items.append({
#                 'product': product,
#                 'quantity': quantity,
#                 'item_total': item_total
#             })
#             cart_total += item_total
#         except Exception as e:
#             logger.error(f"Error retrieving product {product_id}: {str(e)}")
#     return cart_items, cart_total, len(cart_items)

# def home(request):
#     products = Product.objects.all()
#     categories = Prod_category.objects.all()
#     recent_items = Product.objects.order_by('-created_at')[:5]
#     cart_items, cart_total, cart_count = get_cart(request)
#     return render(request, 'home.html', {
#         'products': products,
#         'categories': categories,
#         'recent_items': recent_items,
#         'cart_count': cart_count
#     })

# def register(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             try:
#                 user = form.save()
#                 try:
#                     subject = 'Welcome to Dinesh Ayurvedics!'
#                     message = (
#                         f"Dear {user.mobile_no},\n\n"
#                         f"Welcome to Dinesh Ayurvedics!\n"
#                         f"Your account has been successfully created.\n\n"
#                         f"Phone Number: {user.mobile_no}\n"
#                         f"Login here: https://network-marketing-7llt.onrender.com/\n\n"
#                         f"Best regards,\nDinesh Ayurvedics Team"
#                     )
#                     if user.email:
#                         send_mail(
#                             subject,
#                             message,
#                             settings.DEFAULT_FROM_EMAIL,
#                             [user.email],
#                             fail_silently=False,
#                         )
#                         logger.info(f"Welcome email sent to {user.email}")
#                 except Exception as e:
#                     logger.error(f"Failed to send email to {user.email}: {str(e)}")
#                 messages.success(request, 'Registration successful! Please log in.')
#                 return redirect('login')
#             except Exception as e:
#                 logger.error(f"Error saving user: {str(e)}, Form data: {form.cleaned_data}")
#                 messages.error(request, 'Registration failed due to a server error. Please try again.')
#         else:
#             logger.error(f"Form errors: {form.errors.as_json()}, Form data: {request.POST}")
#             messages.error(request, 'Please correct the errors below.')
#     else:
#         form = CustomUserCreationForm()
    
#     categories = Prod_category.objects.all()
#     recent_items = Product.objects.order_by('-created_at')[:5]
#     cart_items, cart_total, cart_count = get_cart(request)
    
#     return render(request, 'register.html', {
#         'form': form,
#         'categories': categories,
#         'recent_items': recent_items,
#         'cart_count': cart_count
#     })

# def login_view(request):
#     if request.method == 'POST':
#         mobile_no = request.POST.get('mobile_no')
#         password = request.POST.get('password')
#         user = authenticate(request, username=mobile_no, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('home')
#         else:
#             messages.error(request, 'Invalid phone number or password.')
    
#     form = AuthenticationForm()
#     categories = Prod_category.objects.all()
#     recent_items = Product.objects.order_by('-created_at')[:5]
#     cart_items, cart_total, cart_count = get_cart(request)
    
#     return render(request, 'login.html', {
#         'form': form,
#         'categories': categories,
#         'recent_items': recent_items,
#         'cart_count': cart_count
#     })

# def logout_view(request):
#     logout(request)
#     return redirect('login')

# def forgot_password(request):
#     if request.method == 'POST':
#         form = ForgotPasswordForm(request.POST)
#         if form.is_valid():
#             mobile_no = form.cleaned_data['mobile_no']
#             email = form.cleaned_data['email']
#             try:
#                 user = CustomUser.objects.get(mobile_no=mobile_no)
#                 if not user.email and not email:
#                     messages.error(request, 'No email associated with this mobile number. Please provide an email.')
#                     return redirect('forgot_password')
#                 if email:
#                     user.email = email
#                     user.save()
#                 otp_code = ''.join(random.choices(string.digits, k=6))
#                 expires_at = timezone.now() + timezone.timedelta(minutes=5)
#                 OTP.objects.create(user=user, code=otp_code, expires_at=expires_at)
#                 try:
#                     subject = 'Password Reset OTP - Swarna Sampadha'
#                     message = (
#                         f"Dear {user.mobile_no},\n\n"
#                         f"Your OTP for password reset is: {otp_code}\n"
#                         f"This OTP is valid for 5 minutes.\n\n"
#                         f"Best regards,\nSwarna Sampadha Team"
#                     )
#                     send_mail(
#                         subject,
#                         message,
#                         settings.DEFAULT_FROM_EMAIL,
#                         [user.email],
#                         fail_silently=False,
#                     )
#                     logger.info(f"OTP sent to {user.email}")
#                     request.session['reset_mobile_no'] = mobile_no
#                     messages.success(request, 'OTP sent to your email.')
#                     return redirect('verify_otp')
#                 except Exception as e:
#                     logger.error(f"Failed to send OTP to {user.email}: {str(e)}")
#                     messages.error(request, 'Failed to send OTP. Please try again.')
#             except CustomUser.DoesNotExist:
#                 messages.error(request, 'No user found with this mobile number.')
#     else:
#         form = ForgotPasswordForm()
#     categories = Prod_category.objects.all()
#     recent_items = Product.objects.order_by('-created_at')[:5]
#     cart_items, cart_total, cart_count = get_cart(request)
#     return render(request, 'forgot_password.html', {
#         'form': form,
#         'categories': categories,
#         'recent_items': recent_items,
#         'cart_count': cart_count
#     })

# def verify_otp(request):
#     mobile_no = request.session.get('reset_mobile_no')
#     if not mobile_no:
#         messages.error(request, 'Invalid session. Please start the password reset process again.')
#         return redirect('forgot_password')
#     try:
#         user = CustomUser.objects.get(mobile_no=mobile_no)
#     except CustomUser.DoesNotExist:
#         messages.error(request, 'Invalid user. Please start the password reset process again.')
#         return redirect('forgot_password')
    
#     if request.method == 'POST':
#         form = OTPForm(request.POST)
#         if form.is_valid():
#             otp_code = form.cleaned_data['otp']
#             try:
#                 otp = OTP.objects.filter(user=user, code=otp_code).latest('created_at')
#                 if otp.is_valid():
#                     request.session['otp_verified'] = True
#                     messages.success(request, 'OTP verified successfully.')
#                     return redirect('reset_password')
#                 else:
#                     messages.error(request, 'OTP has expired. Please request a new one.')
#             except OTP.DoesNotExist:
#                 messages.error(request, 'Invalid OTP.')
#             except Exception as e:
#                 logger.error(f"Error verifying OTP for {user.mobile_no}: {str(e)}")
#                 messages.error(request, 'Error verifying OTP. Please try again.')
#     else:
#         form = OTPForm()
#     categories = Prod_category.objects.all()
#     recent_items = Product.objects.order_by('-created_at')[:5]
#     cart_items, cart_total, cart_count = get_cart(request)
#     return render(request, 'verify_otp.html', {
#         'form': form,
#         'categories': categories,
#         'recent_items': recent_items,
#         'cart_count': cart_count
#     })

# def reset_password(request):
#     mobile_no = request.session.get('reset_mobile_no')
#     if not mobile_no or not request.session.get('otp_verified'):
#         messages.error(request, 'Invalid session or OTP not verified. Please start the password reset process again.')
#         return redirect('forgot_password')
#     try:
#         user = CustomUser.objects.get(mobile_no=mobile_no)
#     except CustomUser.DoesNotExist:
#         messages.error(request, 'Invalid user. Please start the password reset process again.')
#         return redirect('forgot_password')
    
#     if request.method == 'POST':
#         form = ResetPasswordForm(request.POST)
#         if form.is_valid():
#             try:
#                 user.set_password(form.cleaned_data['new_password1'])
#                 user.save()
#                 OTP.objects.filter(user=user).delete()
#                 del request.session['reset_mobile_no']
#                 del request.session['otp_verified']
#                 messages.success(request, 'Password reset successfully. Please log in.')
#                 return redirect('login')
#             except Exception as e:
#                 logger.error(f"Error resetting password for {user.mobile_no}: {str(e)}")
#                 messages.error(request, 'Error resetting password. Please try again.')
#         else:
#             messages.error(request, 'Please correct the errors below.')
#     else:
#         form = ResetPasswordForm()
#     categories = Prod_category.objects.all()
#     recent_items = Product.objects.order_by('-created_at')[:5]
#     cart_items, cart_total, cart_count = get_cart(request)
#     return render(request, 'reset_password.html', {
#         'form': form,
#         'categories': categories,
#         'recent_items': recent_items,
#         'cart_count': cart_count
#     })

# def product_detail(request, slug):
#     product = get_object_or_404(Product, slug=slug)
#     categories = Prod_category.objects.all()
#     recent_items = Product.objects.order_by('-created_at')[:5]
#     cart_items, cart_total, cart_count = get_cart(request)
#     return render(request, 'product_detail.html', {
#         'product': product,
#         'categories': categories,
#         'recent_items': recent_items,
#         'cart_count': cart_count
#     })

# def contact(request):
#     if request.method == 'POST':
#         form = ContactForm(request.POST)
#         if form.is_valid():
#             try:
#                 subject = f"Contact Form: {form.cleaned_data['subject']}"
#                 message = (
#                     f"Name: {form.cleaned_data['name']}\n"
#                     f"Email: {form.cleaned_data['email']}\n\n"
#                     f"Message:\n{form.cleaned_data['message']}"
#                 )
#                 send_mail(
#                     subject,
#                     message,
#                     settings.DEFAULT_FROM_EMAIL,
#                     [settings.CONTACT_EMAIL],
#                     fail_silently=False,
#                 )
#                 logger.info(f"Contact form email sent from {form.cleaned_data['email']}")
#                 messages.success(request, 'Your message has been sent!')
#                 return redirect('contact')
#             except Exception as e:
#                 logger.error(f"Failed to send contact email: {str(e)}")
#                 messages.error(request, 'Failed to send message. Please try again.')
#     else:
#         form = ContactForm()
#     categories = Prod_category.objects.all()
#     recent_items = Product.objects.order_by('-created_at')[:5]
#     cart_items, cart_total, cart_count = get_cart(request)
#     return render(request, 'contact.html', {
#         'form': form,
#         'categories': categories,
#         'recent_items': recent_items,
#         'cart_count': cart_count
#     })

# def business_plan(request):
#     categories = Prod_category.objects.all()
#     recent_items = Product.objects.order_by('-created_at')[:5]
#     cart_items, cart_total, cart_count = get_cart(request)
#     return render(request, 'business_plan.html', {
#         'categories': categories,
#         'recent_items': recent_items,
#         'cart_count': cart_count
#     })

# def about(request):
#     categories = Prod_category.objects.all()
#     recent_items = Product.objects.order_by('-created_at')[:5]
#     cart_items, cart_total, cart_count = get_cart(request)
#     return render(request, 'about.html', {
#         'categories': categories,
#         'recent_items': recent_items,
#         'cart_count': cart_count
#     })

# def products(request):
#     products = Product.objects.all()
#     categories = Prod_category.objects.all()
#     recent_items = Product.objects.order_by('-created_at')[:5]
#     cart_items, cart_total, cart_count = get_cart(request)
#     return render(request, 'products.html', {
#         'products': products,
#         'categories': categories,
#         'recent_items': recent_items,
#         'cart_count': cart_count
#     })

# def category_products(request, slug):
#     category = get_object_or_404(Prod_category, slug=slug)
#     products = Product.objects.filter(category=category)
#     categories = Prod_category.objects.all()
#     recent_items = Product.objects.order_by('-created_at')[:5]
#     cart_items, cart_total, cart_count = get_cart(request)
#     return render(request, 'products.html', {
#         'products': products,
#         'category': category,
#         'categories': categories,
#         'recent_items': recent_items,
#         'cart_count': cart_count
#     })

# @login_required(login_url='login')
# def add_to_cart(request):
#     if request.method == 'POST':
#         product_id = request.POST.get('product_id')
#         cart = request.session.get('cart', {})
#         cart[product_id] = cart.get(product_id, 0) + 1
#         request.session['cart'] = cart
#         messages.success(request, 'Product added to cart!')
#         return redirect(request.META.get('HTTP_REFERER', 'products'))
#     return redirect('products')

# def remove_from_cart(request):
#     if request.method == 'POST':
#         product_id = request.POST.get('product_id')
#         cart = request.session.get('cart', {})
#         if product_id in cart:
#             del cart[product_id]
#             request.session['cart'] = cart
#             messages.success(request, 'Product removed from cart!')
#         return redirect('cart')
#     return redirect('cart')

# def cart(request):
#     categories = Prod_category.objects.all()
#     recent_items = Product.objects.order_by('-created_at')[:5]
#     cart_items, cart_total, cart_count = get_cart(request)
#     return render(request, 'cart.html', {
#         'cart_items': cart_items,
#         'cart_total': cart_total,
#         'cart_count': cart_count,
#         'categories': categories,
#         'recent_items': recent_items
#     })

# @login_required(login_url='login')
# def payment(request):
#     cart_items, cart_total, cart_count = get_cart(request)
#     if not cart_items:
#         messages.error(request, 'Your cart is empty.')
#         return redirect('cart')
    
#     try:
#         # Validate UPI ID
#         upi_id = getattr(settings, 'OWNER_UPI_ID', None)
#         if not upi_id or not isinstance(upi_id, str) or '@' not in upi_id:
#             raise ValueError("Invalid or missing OWNER_UPI_ID in settings")
        
#         # Generate UPI payment URL
#         upi_url = f"upi://pay?pa={upi_id}&pn=Swarna%20Sampadha&am={cart_total}&cu=INR"
        
#         # Validate cart total
#         if cart_total <= 0:
#             raise ValueError("Cart total must be greater than zero")
        
#         # Generate QR code
#         qr = qrcode.QRCode(
#             version=1,
#             error_correction=qrcode.constants.ERROR_CORRECT_L,
#             box_size=10,
#             border=4
#         )
#         qr.add_data(upi_url)
#         qr.make(fit=True)
#         qr_image = qr.make_image(fill_color="black", back_color="white")
        
#         # Ensure static/images directory exists
#         static_dir = os.path.join(settings.STATICFILES_DIRS[0], 'images')
#         if not os.path.exists(static_dir):
#             os.makedirs(static_dir)
#             logger.info(f"Created directory: {static_dir}")
        
#         # Save QR code to static directory
#         qr_path = os.path.join(static_dir, 'payment_qr.png')
#         qr_image.save(qr_path, format='PNG')
        
#         # Verify file was saved
#         if not os.path.exists(qr_path):
#             raise IOError(f"Failed to save QR code at {qr_path}")
        
#         categories = Prod_category.objects.all()
#         recent_items = Product.objects.order_by('-created_at')[:5]
        
#         return render(request, 'payment.html', {
#             'cart_total': cart_total,
#             'cart_count': cart_count,
#             'categories': categories,
#             'recent_items': recent_items,
#             'qr_code_url': '/static/images/payment_qr.png',
#             'upi_url': upi_url,  # Pass UPI URL to template
#             'owner_mobile_no': settings.OWNER_MOBILE_NO,
#             'owner_email': settings.OWNER_EMAIL,
#         })
#     except Exception as e:
#         exc_type, exc_value, exc_traceback = sys.exc_info()
#         logger.error(f"Error generating payment QR code: {str(e)} (Type: {exc_type.__name__}, File: {exc_traceback.tb_frame.f_code.co_filename}, Line: {exc_traceback.tb_lineno})")
#         messages.error(request, 'Error generating payment QR code. Please try again.')
#         return redirect('cart')

# @login_required(login_url='login')
# def checkout(request):
#     if request.method == 'POST':
#         cart_items, cart_total, cart_count = get_cart(request)
#         if not cart_items:
#             messages.error(request, 'Your cart is empty.')
#             return redirect('cart')
#         try:
#             # Create an Order
#             order = Order.objects.create(
#                 user=request.user,
#                 total_amount=cart_total,
#                 status='success'  # Mark as success upon confirmation
#             )
            
#             # Create OrderItems
#             for item in cart_items:
#                 OrderItem.objects.create(
#                     order=order,
#                     product=item['product'],
#                     quantity=item['quantity'],
#                     item_total=item['item_total']
#                 )
            
#             # Send SMS confirmation
#             sms_message = (
#                 f"Dear {request.user.mobile_no},\n"
#                 f"Your order {order.order_id} for ₹{cart_total} has been placed successfully.\n"
#                 f"Thank you for shopping with Swarna Sampadha!"
#             )
#             sms_response = send_sms([f"+91{request.user.mobile_no}"], sms_message)
#             if sms_response and sms_response.get("type") == "success":
#                 logger.info(f"SMS confirmation sent to {request.user.mobile_no} for order {order.order_id}")
#             else:
#                 logger.error(f"Failed to send SMS confirmation to {request.user.mobile_no}")
            
#             # Clear the cart
#             request.session['cart'] = {}
#             messages.success(request, f'Payment successful! Your order ID is {order.order_id}.')
#             return redirect('recent_purchases')
#         except Exception as e:
#             logger.error(f"Payment processing failed: {str(e)}")
#             messages.error(request, 'Payment failed. Please try again.')
#             return redirect('cart')
#     return redirect('payment')

# @login_required(login_url='login')
# def recent_purchases(request):
#     categories = Prod_category.objects.all()
#     recent_items = Product.objects.order_by('-created_at')[:5]
#     cart_items, cart_total, cart_count = get_cart(request)
    
#     # Fetch user's successful orders, most recent first
#     orders = Order.objects.filter(user=request.user, status='success').order_by('-created_at')
    
#     return render(request, 'recent_purchases.html', {
#         'orders': orders,
#         'categories': categories,
#         'recent_items': recent_items,
#         'cart_count': cart_count
#     })





from hashlib import sha512
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import logging
import random
import string
import uuid
import requests
from .forms import CustomUserCreationForm, ContactForm, ForgotPasswordForm, OTPForm, ResetPasswordForm
from .models import CustomUser, Product, Prod_category, OTP, Order, OrderItem

logger = logging.getLogger(__name__)

def get_cart(request):
    """Retrieve or initialize cart from session."""
    cart = request.session.get('cart', {}) if request.user.is_authenticated else {}
    cart_items = []
    cart_total = 0
    for product_id, quantity in cart.items():
        try:
            product = get_object_or_404(Product, id=product_id)
            item_total = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total
            })
            cart_total += item_total
        except Exception as e:
            logger.error(f"Error retrieving product {product_id}: {str(e)}")
    return cart_items, cart_total, len(cart_items)

def home(request):
    products = Product.objects.all()
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by('-created_at')[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
        'recent_items': recent_items,
        'cart_count': cart_count
    })

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                try:
                    subject = 'Welcome to Dinesh Ayurvedics!'
                    message = (
                        f"Dear {user.mobile_no},\n\n"
                        f"Welcome to Dinesh Ayurvedics!\n"
                        f"Your account has been successfully created.\n\n"
                        f"Phone Number: {user.mobile_no}\n"
                        f"Login here: https://network-marketing-7llt.onrender.com/\n\n"
                        f"Best regards,\nDinesh Ayurvedics Team"
                    )
                    if user.email:
                        send_mail(
                            subject,
                            message,
                            settings.DEFAULT_FROM_EMAIL,
                            [user.email],
                            fail_silently=False,
                        )
                        logger.info(f"Welcome email sent to {user.email}")
                except Exception as e:
                    logger.error(f"Failed to send email to {user.email}: {str(e)}")
                messages.success(request, 'Registration successful! Please log in.')
                return redirect('login')
            except Exception as e:
                logger.error(f"Error saving user: {str(e)}, Form data: {form.cleaned_data}")
                messages.error(request, 'Registration failed due to a server error. Please try again.')
        else:
            logger.error(f"Form errors: {form.errors.as_json()}, Form data: {request.POST}")
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by('-created_at')[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    
    return render(request, 'register.html', {
        'form': form,
        'categories': categories,
        'recent_items': recent_items,
        'cart_count': cart_count
    })

def login_view(request):
    if request.method == 'POST':
        mobile_no = request.POST.get('mobile_no')
        password = request.POST.get('password')
        user = authenticate(request, username=mobile_no, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid phone number or password.')
    
    form = AuthenticationForm()
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by('-created_at')[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    
    return render(request, 'login.html', {
        'form': form,
        'categories': categories,
        'recent_items': recent_items,
        'cart_count': cart_count
    })

def logout_view(request):
    logout(request)
    return redirect('login')

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            mobile_no = form.cleaned_data['mobile_no']
            email = form.cleaned_data['email']
            try:
                user = CustomUser.objects.get(mobile_no=mobile_no)
                if not user.email and not email:
                    messages.error(request, 'No email associated with this mobile number. Please provide an email.')
                    return redirect('forgot_password')
                if email:
                    user.email = email
                    user.save()
                otp_code = ''.join(random.choices(string.digits, k=6))
                expires_at = timezone.now() + timezone.timedelta(minutes=5)
                OTP.objects.create(user=user, code=otp_code, expires_at=expires_at)
                try:
                    subject = 'Password Reset OTP - Swarna Sampadha'
                    message = (
                        f"Dear {user.mobile_no},\n\n"
                        f"Your OTP for password reset is: {otp_code}\n"
                        f"This OTP is valid for 5 minutes.\n\n"
                        f"Best regards,\nSwarna Sampadha Team"
                    )
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    logger.info(f"OTP sent to {user.email}")
                    request.session['reset_mobile_no'] = mobile_no
                    messages.success(request, 'OTP sent to your email.')
                    return redirect('verify_otp')
                except Exception as e:
                    logger.error(f"Failed to send OTP to {user.email}: {str(e)}")
                    messages.error(request, 'Failed to send OTP. Please try again.')
            except CustomUser.DoesNotExist:
                messages.error(request, 'No user found with this mobile number.')
    else:
        form = ForgotPasswordForm()
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by('-created_at')[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(request, 'forgot_password.html', {
        'form': form,
        'categories': categories,
        'recent_items': recent_items,
        'cart_count': cart_count
    })

def verify_otp(request):
    mobile_no = request.session.get('reset_mobile_no')
    if not mobile_no:
        messages.error(request, 'Invalid session. Please start the password reset process again.')
        return redirect('forgot_password')
    try:
        user = CustomUser.objects.get(mobile_no=mobile_no)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Invalid user. Please start the password reset process again.')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp']
            try:
                otp = OTP.objects.filter(user=user, code=otp_code).latest('created_at')
                if otp.is_valid():
                    request.session['otp_verified'] = True
                    messages.success(request, 'OTP verified successfully.')
                    return redirect('reset_password')
                else:
                    messages.error(request, 'OTP has expired. Please request a new one.')
            except OTP.DoesNotExist:
                messages.error(request, 'Invalid OTP.')
            except Exception as e:
                logger.error(f"Error verifying OTP for {user.mobile_no}: {str(e)}")
                messages.error(request, 'Error verifying OTP. Please try again.')
    else:
        form = OTPForm()
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by('-created_at')[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(request, 'verify_otp.html', {
        'form': form,
        'categories': categories,
        'recent_items': recent_items,
        'cart_count': cart_count
    })

def reset_password(request):
    mobile_no = request.session.get('reset_mobile_no')
    if not mobile_no or not request.session.get('otp_verified'):
        messages.error(request, 'Invalid session or OTP not verified. Please start the password reset process again.')
        return redirect('forgot_password')
    try:
        user = CustomUser.objects.get(mobile_no=mobile_no)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Invalid user. Please start the password reset process again.')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            try:
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                OTP.objects.filter(user=user).delete()
                del request.session['reset_mobile_no']
                del request.session['otp_verified']
                messages.success(request, 'Password reset successfully. Please log in.')
                return redirect('login')
            except Exception as e:
                logger.error(f"Error resetting password for {user.mobile_no}: {str(e)}")
                messages.error(request, 'Error resetting password. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ResetPasswordForm()
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by('-created_at')[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(request, 'reset_password.html', {
        'form': form,
        'categories': categories,
        'recent_items': recent_items,
        'cart_count': cart_count
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by('-created_at')[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(request, 'product_detail.html', {
        'product': product,
        'categories': categories,
        'recent_items': recent_items,
        'cart_count': cart_count
    })

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                subject = f"Contact Form: {form.cleaned_data['subject']}"
                message = (
                    f"Name: {form.cleaned_data['name']}\n"
                    f"Email: {form.cleaned_data['email']}\n\n"
                    f"Message:\n{form.cleaned_data['message']}"
                )
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                logger.info(f"Contact form email sent from {form.cleaned_data['email']}")
                messages.success(request, 'Your message has been sent!')
                return redirect('contact')
            except Exception as e:
                logger.error(f"Failed to send contact email: {str(e)}")
                messages.error(request, 'Failed to send message. Please try again.')
    else:
        form = ContactForm()
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by('-created_at')[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(request, 'contact.html', {
        'form': form,
        'categories': categories,
        'recent_items': recent_items,
        'cart_count': cart_count
    })

def business_plan(request):
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by('-created_at')[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(request, 'business_plan.html', {
        'categories': categories,
        'recent_items': recent_items,
        'cart_count': cart_count
    })

def about(request):
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by('-created_at')[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(request, 'about.html', {
        'categories': categories,
        'recent_items': recent_items,
        'cart_count': cart_count
    })

def products(request):
    products = Product.objects.all()
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by('-created_at')[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(request, 'products.html', {
        'products': products,
        'categories': categories,
        'recent_items': recent_items,
        'cart_count': cart_count
    })

def category_products(request, slug):
    category = get_object_or_404(Prod_category, slug=slug)
    products = Product.objects.filter(category=category)
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by('-created_at')[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(request, 'products.html', {
        'products': products,
        'category': category,
        'categories': categories,
        'recent_items': recent_items,
        'cart_count': cart_count
    })

@login_required(login_url='login')
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        cart = request.session.get('cart', {})
        cart[product_id] = cart.get(product_id, 0) + 1
        request.session['cart'] = cart
        messages.success(request, 'Product added to cart!')
        return redirect(request.META.get('HTTP_REFERER', 'products'))
    return redirect('products')

@login_required(login_url='login')
def remove_from_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        cart = request.session.get('cart', {})
        if product_id in cart:
            del cart[product_id]
            request.session['cart'] = cart
            messages.success(request, 'Product removed from cart!')
        return redirect('cart')
    return redirect('cart')

@login_required(login_url='login')
def cart(request):
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by('-created_at')[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'cart_count': cart_count,
        'categories': categories,
        'recent_items': recent_items
    })

@login_required(login_url='login')
def payment(request):
    cart_items, cart_total, cart_count = get_cart(request)
    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        upi_id = request.POST.get('upi_id', '')
        
        try:
            # Validate cart total
            if cart_total <= 0:
                raise ValueError("Cart total must be greater than zero")
            
            # Generate unique transaction ID
            txnid = str(uuid.uuid4().hex)[:20]
            
            # Prepare PayU payment parameters
            payment_data = {
                "key": settings.PAYU_MERCHANT_KEY,
                "txnid": txnid,
                "amount": f"{cart_total:.2f}",
                "productinfo": "Swarna Sampadha Order",
                "firstname": str(request.user.mobile_no),
                "email": str(request.user.email or settings.OWNER_EMAIL),
                "phone": str(request.user.mobile_no),
                "surl": settings.PAYU_SUCCESS_URL,
                "furl": settings.PAYU_FAILURE_URL,
                "service_provider": "payu_paisa",
                "udf1": "",
                "udf2": "",
                "udf3": "",
                "udf4": "",
                "udf5": ""
            }
            
            # Generate PayU hash with the correct parameter order
            hash_string = (
                f"{payment_data['key']}|{payment_data['txnid']}|{payment_data['amount']}|"
                f"{payment_data['productinfo']}|{payment_data['firstname']}|"
                f"{payment_data['email']}|{payment_data['udf1']}|{payment_data['udf2']}|"
                f"{payment_data['udf3']}|{payment_data['udf4']}|{payment_data['udf5']}|"
                f"||||||{settings.PAYU_MERCHANT_SALT}"
            )
            
            payment_data["hash"] = sha512(hash_string.encode()).hexdigest().lower()
            
            # Log payment parameters for debugging
            logger.debug(f"Payment parameters: {payment_data}")
            logger.debug(f"Hash string: {hash_string}")
            logger.debug(f"Generated hash: {payment_data['hash']}")
            
            # Save transaction ID in session for verification
            request.session['payu_txnid'] = payment_data["txnid"]
            request.session['payment_method'] = payment_method
            
            # Add payment method-specific parameters
            if payment_method == 'upi':
                if not upi_id or '@' not in upi_id:
                    messages.error(request, 'Please enter a valid UPI ID.')
                    return redirect('payment')
                payment_data['pg'] = 'UPI'
                payment_data['vpa'] = upi_id
            elif payment_method in ['phonepe', 'gpay', 'paytm']:
                payment_data['pg'] = 'UPI'
                payment_data['bankcode'] = {
                    'phonepe': 'PPBLUPI',
                    'gpay': 'GPAY',
                    'paytm': 'PAYTM'
                }.get(payment_method, 'UPI')
            elif payment_method == 'card':
                payment_data['pg'] = 'CC'
            elif payment_method == 'netbanking':
                payment_data['pg'] = 'NB'
            
            categories = Prod_category.objects.all()
            recent_items = Product.objects.order_by('-created_at')[:5]
            
            return render(request, 'payment.html', {
                'cart_total': cart_total,
                'cart_count': cart_count,
                'categories': categories,
                'recent_items': recent_items,
                'payment_data': payment_data,
                'payu_url': settings.PAYU_BASE_URL,
                'owner_mobile_no': settings.OWNER_MOBILE_NO,
                'owner_email': settings.OWNER_EMAIL,
                'payment_method': payment_method,
                'upi_id': upi_id
            })
        except Exception as e:
            logger.error(f"Error preparing PayU payment: {str(e)}", exc_info=True)
            messages.error(request, 'Error initiating payment. Please try again.')
            return redirect('cart')
    
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by('-created_at')[:5]
    return render(request, 'payment.html', {
        'cart_total': cart_total,
        'cart_count': cart_count,
        'categories': categories,
        'recent_items': recent_items,
        'owner_mobile_no': settings.OWNER_MOBILE_NO,
        'owner_email': settings.OWNER_EMAIL
    })

@csrf_exempt
@login_required(login_url='login')
def payment_success(request):
    if request.method == 'POST':
        response = request.POST
        txnid = response.get('txnid')
        stored_txnid = request.session.get('payu_txnid')
        
        # Verify hash
        hash_string = (
            f"{settings.PAYU_MERCHANT_KEY}|{response.get('txnid')}|{response.get('amount')}|"
            f"{response.get('productinfo')}|{response.get('firstname')}|{response.get('email')}|"
            f"{response.get('udf1', '')}|{response.get('udf2', '')}|{response.get('udf3', '')}|"
            f"{response.get('udf4', '')}|{response.get('udf5', '')}||||||{settings.PAYU_MERCHANT_SALT}"
        )
        calculated_hash = sha512(hash_string.encode()).hexdigest().lower()
        
        if calculated_hash != response.get('hash') or txnid != stored_txnid:
            logger.error(f"Hash mismatch or invalid txnid. Calculated: {calculated_hash}, Received: {response.get('hash')}, Txnid: {txnid}, Stored: {stored_txnid}")
            messages.error(request, 'Invalid transaction. Please try again.')
            return redirect('cart')

        # Verify transaction with PayU
        verification_response = verify_payment(txnid)
        if verification_response and verification_response.get('status') == '1' and verification_response.get('transaction_details', {}).get(txnid, {}).get('status') == 'success':
            cart_items, cart_total, cart_count = get_cart(request)
            try:
                # Create Order
                order = Order.objects.create(
                    user=request.user,
                    total_amount=cart_total,
                    status='success',
                    order_id=txnid  # Use PayU transaction ID
                )
                
                # Create OrderItems
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        quantity=item['quantity'],
                        item_total=item['item_total']
                    )
                
                # Send SMS confirmation
                sms_message = (
                    f"Dear {request.user.mobile_no},\n"
                    f"Your order {order.order_id} for ₹{cart_total} has been placed successfully.\n"
                    f"Thank you for shopping with Swarna Sampadha!"
                )
                sms_response = send_sms([f"+91{request.user.mobile_no}"], sms_message)
                if sms_response and sms_response.get("type") == "success":
                    logger.info(f"SMS confirmation sent to {request.user.mobile_no} for order {order.order_id}")
                else:
                    logger.error(f"Failed to send SMS confirmation to {request.user.mobile_no}")
                
                # Clear the cart
                request.session['cart'] = {}
                if 'payu_txnid' in request.session:
                    del request.session['payu_txnid']
                if 'payment_method' in request.session:
                    del request.session['payment_method']
                messages.success(request, f'Payment successful! Your order ID is {order.order_id}.')
                return redirect('recent_purchases')
            except Exception as e:
                logger.error(f"Payment processing failed: {str(e)}")
                messages.error(request, 'Payment processing failed. Please contact support.')
                return redirect('cart')
        else:
            logger.error(f"Payment verification failed for txnid {txnid}: {verification_response}")
            messages.error(request, 'Payment verification failed. Please try again.')
            return redirect('cart')
    return redirect('cart')

@csrf_exempt
@login_required(login_url='login')
def payment_failure(request):
    if request.method == 'POST':
        response = request.POST
        logger.error(f"Payment failed: {response.get('error_Message', 'Unknown error')}")
        messages.error(request, f'Payment failed: {response.get("error_Message", "Unknown error")}')
        if 'payu_txnid' in request.session:
            del request.session['payu_txnid']
        if 'payment_method' in request.session:
            del request.session['payment_method']
    return redirect('cart')

@login_required(login_url='login')
def checkout(request):
    return redirect('payment')

@login_required(login_url='login')
def recent_purchases(request):
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by('-created_at')[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    
    # Fetch user's successful orders, most recent first
    orders = Order.objects.filter(user=request.user, status='success').order_by('-created_at')
    
    return render(request, 'recent_purchases.html', {
        'orders': orders,
        'categories': categories,
        'recent_items': recent_items,
        'cart_count': cart_count
    })

def send_sms(mobile_numbers, message):
    """
    Send SMS using MSG91 API.
    :param mobile_numbers: List of mobile numbers (with country code, e.g., ['+919999999999'])
    :param message: The message to send
    :return: Response from MSG91 API
    """
    url = "https://api.msg91.com/api/v2/sendsms"
    payload = {
        "sender": settings.MSG91_SENDER_ID,
        "route": "4",  # Transactional SMS route
        "country": "91",  # Country code for India
        "sms": [
            {
                "message": message,
                "to": mobile_numbers
            }
        ]
    }
    headers = {
        "authkey": settings.MSG91_AUTH_KEY,
        "content-type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        logger.info(f"SMS sent successfully: {response.json()}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error sending SMS: {e}")
        return None

def verify_payment(txnid):
    """Verify transaction status with PayU."""
    try:
        url = "https://info.payu.in/merchant/postservice?form=2"
        payload = {
            "key": settings.PAYU_MERCHANT_KEY,
            "command": "verify_payment",
            "var1": txnid,
            "hash": sha512(
                f"{settings.PAYU_MERCHANT_KEY}|verify_payment|{txnid}|||||||||{settings.PAYU_MERCHANT_SALT}"
                .encode()
            ).hexdigest().lower()
        }
        response = requests.post(url, data=payload)
        response_data = response.json()
        logger.debug(f"Verification response for txnid {txnid}: {response_data}")
        return response_data
    except Exception as e:
        logger.error(f"Error verifying payment for txnid {txnid}: {str(e)}")
        return None