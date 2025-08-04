from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, ContactForm
from .models import CustomUser, Product
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, user=request.user if request.user.is_authenticated else None)
        if form.is_valid():
            user = form.save()
            try:
                # Send welcome email
                subject = 'Welcome to Network Marketing!'
                message = (
                    f"Dear {user.username},\n\n"
                    f"Welcome to our Network Marketing platform!\n"
                    f"Your account has been successfully created.\n\n"
                    f"Username: {user.username}\n"
                    f"Password: {form.cleaned_data['password1']}\n"
                    f"Login here: http://127.0.0.1:8000/login/\n\n"
                    f"Best regards,\nNetwork Marketing Team"
                )
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
            if request.user.is_authenticated:
                messages.success(request, f"Successfully registered {user.username}.")
                return redirect('dashboard')
            else:
                messages.success(request, 'Registration successful! Please log in.')
                return redirect('login')
        else:
            logger.error(f"Form errors: {form.errors}")
    else:
        form = CustomUserCreationForm(user=request.user if request.user.is_authenticated else None)
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    user = request.user
    # Get direct referrals (users where introducer is the current user)
    direct_referrals = CustomUser.objects.filter(introducer=user)
    # Get all team members (direct and indirect)
    def get_team(user, team=None):
        if team is None:
            team = []
        children = CustomUser.objects.filter(parent=user)
        for child in children:
            team.append(child)
            get_team(child, team)
        return team
    team_members = get_team(user)
    form = CustomUserCreationForm(user=user)  # Form for registering new users
    return render(request, 'dashboard.html', {
        'referral_count': direct_referrals.count(),
        'direct_referrals': direct_referrals,
        'team_members': team_members,
        'form': form,
    })

@login_required
def user_referrals(request, username):
    user = get_object_or_404(CustomUser, username=username)
    # Ensure the user can only view their own team
    def get_team(current_user, team=None):
        if team is None:
            team = []
        children = CustomUser.objects.filter(parent=current_user)
        for child in children:
            team.append(child)
            get_team(child, team)
        return team
    if user != request.user and user not in get_team(request.user):
        messages.error(request, "You don't have permission to view this user's referrals.")
        return redirect('dashboard')
    direct_referrals = CustomUser.objects.filter(introducer=user)
    team_members = get_team(user)
    return render(request, 'user_referrals.html', {
        'selected_user': user,
        'direct_referrals': direct_referrals,
        'team_members': team_members,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'product_detail.html', {'product': product})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Your message has been sent!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

def business_plan(request):
    return render(request, 'business_plan.html')

@login_required
def tree(request):
    users = CustomUser.objects.all()
    return render(request, 'tree.html', {'users': users})

def about(request):
    return render(request, 'about.html')

def products(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})