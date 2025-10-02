from hashlib import sha512
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import logging
import random
import string
import uuid
import requests
import qrcode
import os
from .forms import (
    AddressForm,
    MobileNumberForm,
    OTPForm,
    UserProfileForm,
    ContactForm,
    ForgotPasswordForm,
    ResetPasswordForm,
)
from .models import CustomUser, Product, Prod_category, OTP, Order, OrderItem, Address
from .utils import send_sms

logger = logging.getLogger(__name__)


def get_cart(request):
    """Retrieve or initialize cart from session."""
    cart = request.session.get("cart", {}) if request.user.is_authenticated else {}
    cart_items = []
    cart_total = 0
    for product_id, quantity in cart.items():
        try:
            product = get_object_or_404(Product, id=product_id)
            item_total = product.price * quantity
            cart_items.append(
                {"product": product, "quantity": quantity, "item_total": item_total}
            )
            cart_total += item_total
        except Exception as e:
            logger.error(f"Error retrieving product {product_id}: {str(e)}")
    return cart_items, cart_total, len(cart_items)


def home(request):
    products = Product.objects.all()
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by("-created_at")[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(
        request,
        "home.html",
        {
            "products": products,
            "categories": categories,
            "recent_items": recent_items,
            "cart_count": cart_count,
        },
    )


def login_view(request):
    if request.method == "POST":
        form = MobileNumberForm(request.POST)
        if form.is_valid():
            mobile_no = form.cleaned_data["mobile_no"]

            # Validate mobile number format
            if len(mobile_no) != 10 or not mobile_no.isdigit():
                messages.error(request, "Please enter a valid 10-digit mobile number.")
                return redirect("login")

            # Check if user exists
            try:
                user = CustomUser.objects.get(mobile_no=mobile_no)
                is_new_user = False
            except CustomUser.DoesNotExist:
                # Create new user
                user = CustomUser.objects.create_user(mobile_no=mobile_no)
                is_new_user = True

            # Generate OTP
            otp_code = "".join(random.choices(string.digits, k=6))
            expires_at = timezone.now() + timezone.timedelta(minutes=5)

            # Create OTP record
            OTP.objects.create(
                user=user if not is_new_user else None,
                mobile_no=mobile_no,
                code=otp_code,
                expires_at=expires_at,
            )

            # Send OTP via SMS
            sms_message = f"Your OTP for Ayurvedics login is: {otp_code}. This OTP is valid for 5 minutes."
            mobile_no_with_cc = "+91" + mobile_no  # Always add country code

            # Send OTP via SMS with better error handling
            sms_response = send_sms([mobile_no_with_cc], sms_message)

            # Debug: Print OTP to console for testing
            print(f"OTP for {mobile_no}: {otp_code}")
            logger.info(f"Generated OTP for {mobile_no}: {otp_code}")

            if sms_response and sms_response.get("type") == "success":
                request.session["login_mobile_no"] = mobile_no
                request.session["is_new_user"] = is_new_user
                messages.success(request, "OTP sent to your mobile number.")
                return redirect("verify_otp")
            else:
                error_msg = sms_response.get("error", "Failed to send OTP.")
                # Even if SMS fails, allow user to proceed with OTP (for testing)
                request.session["login_mobile_no"] = mobile_no
                request.session["is_new_user"] = is_new_user
                messages.warning(
                    request,
                    f"SMS may have failed: {error_msg}. OTP: {otp_code} (check console for testing)",
                )
                return redirect("verify_otp")
        else:
            messages.error(request, "Please enter a valid mobile number.")
    else:
        form = MobileNumberForm()

    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by("-created_at")[:5]
    cart_items, cart_total, cart_count = get_cart(request)

    return render(
        request,
        "login.html",
        {
            "form": form,
            "categories": categories,
            "recent_items": recent_items,
            "cart_count": cart_count,
        },
    )


def verify_otp(request):
    mobile_no = request.session.get("login_mobile_no")
    is_new_user = request.session.get("is_new_user", False)

    if not mobile_no:
        messages.error(
            request, "Invalid session. Please start the login process again."
        )
        return redirect("login")

    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data["otp"]
            try:
                # Get the latest OTP for this mobile number
                otp = OTP.objects.filter(mobile_no=mobile_no, is_used=False).latest(
                    "created_at"
                )

                if otp.is_valid() and otp.code == otp_code:
                    # Mark OTP as used
                    otp.is_used = True
                    otp.save()

                    # Get or create user
                    if is_new_user:
                        user = CustomUser.objects.get(mobile_no=mobile_no)
                        # New user - redirect to profile completion
                        login(request, user)
                        messages.success(
                            request,
                            "OTP verified successfully! Please complete your profile.",
                        )
                        return redirect("complete_profile")
                    else:
                        # Existing user - login directly
                        user = CustomUser.objects.get(mobile_no=mobile_no)
                        login(request, user)
                        messages.success(request, "Login successful!")
                        return redirect("home")
                else:
                    if not otp.is_valid():
                        messages.error(
                            request, "OTP has expired. Please request a new one."
                        )
                    else:
                        messages.error(request, "Invalid OTP.")
            except OTP.DoesNotExist:
                messages.error(request, "Invalid OTP or OTP not found.")
            except Exception as e:
                logger.error(f"Error verifying OTP for {mobile_no}: {str(e)}")
                messages.error(request, "Error verifying OTP. Please try again.")
    else:
        form = OTPForm()

    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by("-created_at")[:5]
    cart_items, cart_total, cart_count = get_cart(request)

    return render(
        request,
        "verify_otp.html",
        {
            "form": form,
            "mobile_no": mobile_no,
            "categories": categories,
            "recent_items": recent_items,
            "cart_count": cart_count,
        },
    )


@login_required(login_url="login")
def complete_profile(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("products")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserProfileForm(instance=request.user)

    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by("-created_at")[:5]
    cart_items, cart_total, cart_count = get_cart(request)

    return render(
        request,
        "complete_profile.html",
        {
            "form": form,
            "categories": categories,
            "recent_items": recent_items,
            "cart_count": cart_count,
        },
    )


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")


def forgot_password(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            mobile_no = form.cleaned_data["mobile_no"]
            email = form.cleaned_data["email"]
            try:
                user = CustomUser.objects.get(mobile_no=mobile_no)
                if not user.email and not email:
                    messages.error(
                        request,
                        "No email associated with this mobile number. Please provide an email.",
                    )
                    return redirect("forgot_password")
                if email:
                    user.email = email
                    user.save()
                otp_code = "".join(random.choices(string.digits, k=6))
                expires_at = timezone.now() + timezone.timedelta(minutes=5)
                OTP.objects.create(
                    user=user, mobile_no=mobile_no, code=otp_code, expires_at=expires_at
                )
                try:
                    subject = "Password Reset OTP - Ayurvedics"
                    message = (
                        f"Dear {user.mobile_no},\n\n"
                        f"Your OTP for password reset is: {otp_code}\n"
                        f"This OTP is valid for 5 minutes.\n\n"
                        f"Best regards,\nAyurvedics Team"
                    )
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    logger.info(f"OTP sent to {user.email}")
                    request.session["reset_mobile_no"] = mobile_no
                    messages.success(request, "OTP sent to your email.")
                    return redirect("verify_otp")
                except Exception as e:
                    logger.error(f"Failed to send OTP to {user.email}: {str(e)}")
                    messages.error(request, "Failed to send OTP. Please try again.")
            except CustomUser.DoesNotExist:
                messages.error(request, "No user found with this mobile number.")
    else:
        form = ForgotPasswordForm()
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by("-created_at")[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(
        request,
        "forgot_password.html",
        {
            "form": form,
            "categories": categories,
            "recent_items": recent_items,
            "cart_count": cart_count,
        },
    )


def reset_password(request):
    mobile_no = request.session.get("reset_mobile_no")
    if not mobile_no:
        messages.error(
            request,
            "Invalid session. Please start the password reset process again.",
        )
        return redirect("forgot_password")
    try:
        user = CustomUser.objects.get(mobile_no=mobile_no)
    except CustomUser.DoesNotExist:
        messages.error(
            request, "Invalid user. Please start the password reset process again."
        )
        return redirect("forgot_password")

    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            try:
                user.set_password(form.cleaned_data["new_password1"])
                user.save()
                OTP.objects.filter(user=user).delete()
                del request.session["reset_mobile_no"]
                messages.success(request, "Password reset successfully. Please log in.")
                return redirect("login")
            except Exception as e:
                logger.error(f"Error resetting password for {user.mobile_no}: {str(e)}")
                messages.error(request, "Error resetting password. Please try again.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ResetPasswordForm()
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by("-created_at")[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(
        request,
        "reset_password.html",
        {
            "form": form,
            "categories": categories,
            "recent_items": recent_items,
            "cart_count": cart_count,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by("-created_at")[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(
        request,
        "product_detail.html",
        {
            "product": product,
            "categories": categories,
            "recent_items": recent_items,
            "cart_count": cart_count,
        },
    )


def contact(request):
    if request.method == "POST":
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
                logger.info(
                    f"Contact form email sent from {form.cleaned_data['email']}"
                )
                messages.success(request, "Your message has been sent!")
                return redirect("contact")
            except Exception as e:
                logger.error(f"Failed to send contact email: {str(e)}")
                messages.error(request, "Failed to send message. Please try again.")
    else:
        form = ContactForm()
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by("-created_at")[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(
        request,
        "contact.html",
        {
            "form": form,
            "categories": categories,
            "recent_items": recent_items,
            "cart_count": cart_count,
        },
    )


def business_plan(request):
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by("-created_at")[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(
        request,
        "business_plan.html",
        {
            "categories": categories,
            "recent_items": recent_items,
            "cart_count": cart_count,
        },
    )


def about(request):
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by("-created_at")[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(
        request,
        "about.html",
        {
            "categories": categories,
            "recent_items": recent_items,
            "cart_count": cart_count,
        },
    )


def products(request):
    products = Product.objects.all()
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by("-created_at")[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(
        request,
        "products.html",
        {
            "products": products,
            "categories": categories,
            "recent_items": recent_items,
            "cart_count": cart_count,
        },
    )


def category_products(request, slug):
    category = get_object_or_404(Prod_category, slug=slug)
    products = Product.objects.filter(category=category)
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by("-created_at")[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    return render(
        request,
        "products.html",
        {
            "products": products,
            "category": category,
            "categories": categories,
            "recent_items": recent_items,
            "cart_count": cart_count,
        },
    )


@login_required(login_url="login")
def add_to_cart(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))
        cart = request.session.get("cart", {})
        cart[product_id] = cart.get(product_id, 0) + quantity
        request.session["cart"] = cart
        messages.success(request, "Product added to cart!")
        return redirect(request.META.get("HTTP_REFERER", "products"))
    return redirect("products")


@login_required(login_url="login")
def remove_from_cart(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        cart = request.session.get("cart", {})
        if product_id in cart:
            del cart[product_id]
            request.session["cart"] = cart
            messages.success(request, "Product removed from cart!")
        return redirect("cart")
    return redirect("cart")


@login_required(login_url="login")
def cart(request):
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by("-created_at")[:5]
    cart_items, cart_total, cart_count = get_cart(request)
    addresses = Address.objects.filter(user=request.user)
    address_form = AddressForm()
    selected_address = addresses.filter(is_selected=True).first()
    return render(
        request,
        "cart.html",
        {
            "cart_items": cart_items,
            "cart_total": cart_total,
            "cart_count": cart_count,
            "categories": categories,
            "recent_items": recent_items,
            "addresses": addresses,
            "address_form": address_form,
            "selected_address": selected_address,
        },
    )


@login_required(login_url="login")
def proceed_to_payment(request):
    cart_items, cart_total, cart_count = get_cart(request)
    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    # Generate QR code for UPI payment
    upi_id = settings.OWNER_UPI_ID
    upi_url = f"upi://pay?pa={upi_id}&pn=Dinesh%20Ayurvedics&am={cart_total}&cu=INR"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(upi_url)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")

    # Save QR code to media directory
    qr_path = os.path.join(
        settings.MEDIA_ROOT, "qr_codes", f"payment_{request.user.id}.png"
    )
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)
    qr_image.save(qr_path)

    # URL for template
    qr_url = f"{settings.MEDIA_URL}qr_codes/payment_{request.user.id}.png"

    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by("-created_at")[:5]

    return render(
        request,
        "payment.html",
        {
            "cart_total": cart_total,
            "owner_mobile_no": settings.OWNER_MOBILE_NO,
            "owner_email": settings.OWNER_EMAIL,
            "owner_upi_id": settings.OWNER_UPI_ID,
            "qr_url": qr_url,
            "categories": categories,
            "recent_items": recent_items,
            "cart_count": cart_count,
        },
    )


@csrf_exempt
@login_required(login_url="login")
def payment_success(request):
    if request.method == "POST":
        cart_items, cart_total, cart_count = get_cart(request)
        try:
            # Create Order
            order = Order.objects.create(
                user=request.user,
                total_amount=cart_total,
                status="success",
                order_id=f"ORDER_{request.user.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}",
            )

            # Create OrderItems
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    quantity=item["quantity"],
                    item_total=item["item_total"],
                )

            # Send SMS confirmation
            sms_message = (
                f"Dear {request.user.mobile_no},\n"
                f"Your order {order.order_id} for ₹{cart_total} has been placed successfully.\n"
                f"Thank you for shopping with Ayurvedics!"
            )
            sms_response = send_sms([f"+91{request.user.mobile_no}"], sms_message)
            if sms_response and sms_response.get("type") == "success":
                logger.info(
                    f"SMS confirmation sent to {request.user.mobile_no} for order {order.order_id}"
                )
            else:
                logger.error(
                    f"Failed to send SMS confirmation to {request.user.mobile_no}"
                )

            # Clear the cart
            request.session["cart"] = {}
            messages.success(
                request, f"Payment successful! Your order ID is {order.order_id}."
            )
            return redirect("recent_purchases")
        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")
            messages.error(
                request, "Payment processing failed. Please contact support."
            )
            return redirect("cart")
    return redirect("cart")


@csrf_exempt
@login_required(login_url="login")
def payment_failure(request):
    if request.method == "POST":
        response = request.POST
        logger.error(
            f"Payment failed: {response.get('error_Message', 'Unknown error')}"
        )
        messages.error(
            request, f'Payment failed: {response.get("error_Message", "Unknown error")}'
        )
        if "payu_txnid" in request.session:
            del request.session["payu_txnid"]
        if "payment_method" in request.session:
            del request.session["payment_method"]
    return redirect("cart")


@login_required(login_url="login")
def checkout(request):
    return redirect("payment")


@login_required(login_url="login")
def recent_purchases(request):
    categories = Prod_category.objects.all()
    recent_items = Product.objects.order_by("-created_at")[:5]
    cart_items, cart_total, cart_count = get_cart(request)

    # Fetch user's successful orders, most recent first
    orders = Order.objects.filter(user=request.user, status="success").order_by(
        "-created_at"
    )

    return render(
        request,
        "recent_purchases.html",
        {
            "orders": orders,
            "categories": categories,
            "recent_items": recent_items,
            "cart_count": cart_count,
        },
    )


@login_required(login_url="login")
def add_address(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Address added!")
        else:
            messages.error(request, "Invalid address.")
    return redirect("cart")


@login_required(login_url="login")
def select_address(request, address_id):
    Address.objects.filter(user=request.user).update(is_selected=False)
    Address.objects.filter(id=address_id, user=request.user).update(is_selected=True)
    messages.success(request, "Address selected!")
    return redirect("cart")


# def send_sms(mobile_numbers, message):
#     """
#     Send SMS using MSG91 API.
#     :param mobile_numbers: List of mobile numbers (with country code, e.g., ['+919999999999'])
#     :param message: The message to send
#     :return: Response from MSG91 API
#     """
#     # If MSG91 is not configured, log and return success for testing
#     if not hasattr(settings, "MSG91_AUTH_KEY") or not settings.MSG91_AUTH_KEY:
#         logger.warning("MSG91 not configured - simulating SMS send")
#         print(f"SIMULATED SMS to {mobile_numbers}: {message}")  # For debugging
#         return {"type": "success", "message": "SMS simulated - MSG91 not configured"}

#     url = "https://api.msg91.com/api/v5/flow/"  # Updated to v5 API
#     payload = {
#         "template_id": getattr(
#             settings, "MSG91_TEMPLATE_ID", None
#         ),  # Add template ID if using templates
#         "short_url": "0",  # Disable URL shortening
#         "recipients": [
#             {
#                 "mobiles": mobile_numbers[0] if mobile_numbers else "",
#                 "VAR1": message,  # Use variable for dynamic content
#             }
#         ],
#     }

#     headers = {"authkey": settings.MSG91_AUTH_KEY, "content-type": "application/json"}

#     try:
#         response = requests.post(url, json=payload, headers=headers)
#         response_data = response.json()

#         # Check MSG91 specific success conditions
#         if response.status_code == 200:
#             if response_data.get("type") == "success":
#                 logger.info(f"SMS sent successfully: {response_data}")
#                 return {"type": "success", "data": response_data}
#             else:
#                 logger.error(f"MSG91 API error: {response_data}")
#                 return {
#                     "type": "error",
#                     "error": response_data.get("message", "Unknown error"),
#                 }
#         else:
#             logger.error(f"MSG91 HTTP error {response.status_code}: {response_data}")
#             return {"type": "error", "error": f"HTTP {response.status_code}"}

#     except requests.RequestException as e:
#         logger.error(f"Error sending SMS: {e}")
#         return {"type": "error", "error": str(e)}


@login_required(login_url="login")
def upload_payment_screenshot(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if request.method == "POST" and request.FILES.get("payment_screenshot"):
        screenshot = request.FILES["payment_screenshot"]
        for item in order.orderitem_set.all():
            item.payment_screenshot = screenshot
            item.save()
        order.status = "pending"
        order.save()
        messages.success(request, "Screenshot uploaded. Awaiting admin confirmation.")
    return redirect("recent_purchases")


@login_required(login_url="login")
def mark_delivered(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    if request.method == "POST":
        item.status = "delivered"
        item.save()
        messages.success(request, "Product marked as delivered!")
    return redirect("recent_purchases")


@csrf_exempt
def resend_otp(request):
    if request.method == "POST":
        import json

        data = json.loads(request.body)
        mobile_no = data.get("mobile_no")

        if not mobile_no:
            return JsonResponse({"success": False, "error": "Mobile number required."})

        try:
            # Get or create user
            try:
                user = CustomUser.objects.get(mobile_no=mobile_no)
            except CustomUser.DoesNotExist:
                user = CustomUser.objects.create_user(mobile_no=mobile_no)

            # Generate new OTP
            otp_code = "".join(random.choices(string.digits, k=6))
            expires_at = timezone.now() + timezone.timedelta(minutes=5)

            # Create OTP record
            OTP.objects.create(
                user=user,
                mobile_no=mobile_no,
                code=otp_code,
                expires_at=expires_at,
            )

            # Send SMS
            sms_message = f"Your OTP for Swarna Sampadha login is: {otp_code}. This OTP is valid for 5 minutes."
            mobile_no_with_cc = "+91" + mobile_no

            sms_response = send_sms([mobile_no_with_cc], sms_message)

            # Debug: Print OTP to console
            print(f"Resent OTP for {mobile_no}: {otp_code}")
            logger.info(f"Resent OTP for {mobile_no}: {otp_code}")

            if sms_response and sms_response.get("type") == "success":
                return JsonResponse({"success": True})
            else:
                # Even if SMS fails, return success with warning
                return JsonResponse(
                    {
                        "success": True,
                        "warning": "SMS may have failed, but OTP was generated. Check console for OTP.",
                        "debug_otp": otp_code,  # Remove this in production
                    }
                )

        except Exception as e:
            logger.error(f"Error in resend_otp: {str(e)}")
            return JsonResponse({"success": False, "error": "Internal server error."})

    return JsonResponse({"success": False, "error": "Invalid request method."})


def send_sms(mobile_numbers, message):
    """
    Send SMS using MSG91 API with template support.
    :param mobile_numbers: List of mobile numbers (with country code, e.g., ['+919999999999'])
    :param message: The OTP code to send
    :return: Response from MSG91 API
    """
    # If MSG91 is not configured, log and return success for testing
    if not hasattr(settings, "MSG91_AUTH_KEY") or not settings.MSG91_AUTH_KEY:
        logger.warning("MSG91 not configured - simulating SMS send")
        print(f"SIMULATED SMS to {mobile_numbers}: {message}")
        return {"type": "success", "message": "SMS simulated - MSG91 not configured"}

    template_id = getattr(settings, "MSG91_TEMPLATE_ID", None)
    if not template_id:
        logger.error("MSG91_TEMPLATE_ID not configured")
        return {"type": "error", "error": "Template ID missing"}

    # Extract just the OTP code from the message (in case full message is passed)
    otp_code = message
    if "OTP" in message:
        # Extract OTP code if full message is passed
        import re

        otp_match = re.search(r"(\d{6})", message)
        if otp_match:
            otp_code = otp_match.group(1)

    url = "https://control.msg91.com/api/v5/flow/"
    payload = {
        "flow_id": template_id,  # MSG91 uses 'flow_id' instead of 'template_id'
        "recipients": [
            {
                "mobiles": (
                    mobile_numbers[0].replace("+", "") if mobile_numbers else ""
                ),  # Remove + for MSG91
                "OTP": otp_code,  # This matches your template variable ##OTP##
            }
        ],
    }

    headers = {"authkey": settings.MSG91_AUTH_KEY, "Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        # Check MSG91 specific success conditions
        if response.status_code == 200:
            if response_data.get("type") == "success":
                logger.info(f"SMS sent successfully: {response_data}")
                return {"type": "success", "data": response_data}
            else:
                logger.error(f"MSG91 API error: {response_data}")
                return {
                    "type": "error",
                    "error": response_data.get("message", "Unknown error"),
                }
        else:
            logger.error(f"MSG91 HTTP error {response.status_code}: {response_data}")
            return {"type": "error", "error": f"HTTP {response.status_code}"}

    except requests.RequestException as e:
        logger.error(f"Error sending SMS: {e}")
        return {"type": "error", "error": str(e)}


@login_required(login_url="login")
def delete_address(request, address_id):
    if request.method == "POST":
        try:
            address = get_object_or_404(Address, id=address_id, user=request.user)
            address.delete()
            messages.success(request, "Address deleted successfully!")
        except Address.DoesNotExist:
            messages.error(request, "Address not found.")
        return redirect("cart")
    return redirect("cart")


@csrf_exempt
@login_required(login_url="login")
def update_cart_quantity(request):
    if request.method == "POST":
        import json

        data = json.loads(request.body)
        product_id = str(data.get("product_id"))
        action = data.get("action")

        cart = request.session.get("cart", {})

        if product_id in cart:
            if action == "increment":
                cart[product_id] += 1
            elif action == "decrement" and cart[product_id] > 1:
                cart[product_id] -= 1
            elif action == "remove":
                del cart[product_id]

            request.session["cart"] = cart
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "Product not in cart."})

    return JsonResponse({"success": False, "error": "Invalid request method."})


