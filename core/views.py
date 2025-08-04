from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, ContactForm, ForgotPasswordForm, OTPForm, ResetPasswordForm
from .models import CustomUser, Product, Prod_category, OTP
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import logging
import random
import string
import qrcode
import os
import sys
from PIL import Image

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
                    subject = 'Welcome to Swarna Sampadha!'
                    message = (
                        f"Dear {user.mobile_no},\n\n"
                        f"Welcome to Swarna Sampadha!\n"
                        f"Your account has been successfully created.\n\n"
                        f"Phone Number: {user.mobile_no}\n"
                        f"Login here: http://127.0.0.1:8000/login/\n\n"
                        f"Best regards,\nSwarna Sampadha Team"
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
            try:
                user = CustomUser.objects.get(mobile_no=mobile_no)
                if not user.email:
                    messages.error(request, 'No email associated with this mobile number.')
                    return redirect('forgot_password')
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
    
    try:
        # Validate UPI ID
        upi_id = getattr(settings, 'OWNER_UPI_ID', None)
        if not upi_id or not isinstance(upi_id, str) or '@' not in upi_id:
            raise ValueError("Invalid or missing OWNER_UPI_ID in settings")
        
        # Generate UPI payment URL
        upi_url = f"upi://pay?pa={upi_id}&pn=Swarna%20Sampadha&am={cart_total}&cu=INR"
        
        # Validate cart total
        if cart_total <= 0:
            raise ValueError("Cart total must be greater than zero")
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(upi_url)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Ensure static/images directory exists
        static_dir = os.path.join(settings.STATICFILES_DIRS[0], 'images')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
            logger.info(f"Created directory: {static_dir}")
        
        # Save QR code to static directory
        qr_path = os.path.join(static_dir, 'payment_qr.png')
        qr_image.save(qr_path, format='PNG')
        
        # Verify file was saved
        if not os.path.exists(qr_path):
            raise IOError(f"Failed to save QR code at {qr_path}")
        
        categories = Prod_category.objects.all()
        recent_items = Product.objects.order_by('-created_at')[:5]
        
        return render(request, 'payment.html', {
            'cart_total': cart_total,
            'cart_count': cart_count,
            'categories': categories,
            'recent_items': recent_items,
            'qr_code_url': '/static/images/payment_qr.png',
            'owner_mobile_no': settings.OWNER_MOBILE_NO,
            'owner_email': settings.OWNER_EMAIL,
        })
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error(f"Error generating payment QR code: {str(e)} (Type: {exc_type.__name__}, File: {exc_traceback.tb_frame.f_code.co_filename}, Line: {exc_traceback.tb_lineno})")
        messages.error(request, 'Error generating payment QR code. Please try again.')
        return redirect('cart')

@login_required(login_url='login')
def checkout(request):
    if request.method == 'POST':
        cart_items, cart_total, cart_count = get_cart(request)
        if not cart_items:
            messages.error(request, 'Your cart is empty.')
            return redirect('cart')
        try:
            # Clear the cart after payment confirmation
            request.session['cart'] = {}
            messages.success(request, 'Payment successful! Your order has been placed.')
            return redirect('products')
        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")
            messages.error(request, 'Payment failed. Please try again.')
            return redirect('cart')
    return redirect('payment')