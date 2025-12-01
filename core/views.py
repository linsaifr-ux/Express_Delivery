from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from .models import User, Package, TrackingEvent, CustomerProfile
from .forms import PackageForm, CustomUserCreationForm, UserUpdateForm, CustomerProfileForm

from django.views.i18n import set_language
from django.urls import translate_url

def set_language_custom(request):
    response = set_language(request)
    if response.status_code == 302:
        next_url = response.url
        # If the response is a redirect, translate the URL to the selected language
        if request.method == 'POST':
            lang_code = request.POST.get('language')
            if lang_code and next_url:
                if next_url == '/':
                    response['Location'] = f'/{lang_code}/'
                else:
                    translated_url = translate_url(next_url, lang_code)
                    if translated_url:
                        response['Location'] = translated_url
    return response

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create default customer profile
            CustomerProfile.objects.create(user=user, address='Update your address', phone_number='Update phone')
            
            login(request, user)
            messages.success(request, _('Registration successful!'))
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def track_package(request):
    tracking_number = request.GET.get('tracking_number')
    package = None
    if tracking_number:
        try:
            package = Package.objects.get(tracking_number=tracking_number)
        except Package.DoesNotExist:
            messages.error(request, _('Package with tracking number %(tracking_number)s not found.') % {'tracking_number': tracking_number})
    
    return render(request, 'tracking/track.html', {'package': package, 'tracking_number': tracking_number})

@login_required
def create_package(request):
    if request.method == 'POST':
        form = PackageForm(request.POST, user=request.user)
        if form.is_valid():
            package = form.save(commit=False)
            package.sender = request.user
            package.save()
            
            # Initial tracking event is now handled by signals
            
            messages.success(request, _('Package created successfully! Tracking Number: %(tracking_number)s') % {'tracking_number': package.tracking_number})
            return redirect('track_package')
    else:
        form = PackageForm(user=request.user)
    
    return render(request, 'package/create.html', {'form': form})

@login_required
def dashboard(request):
    packages = Package.objects.filter(sender=request.user).order_by('-created_at')
    return render(request, 'core/dashboard.html', {'packages': packages})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        # Ensure customer profile exists
        if not hasattr(request.user, 'customer_profile'):
            CustomerProfile.objects.create(user=request.user, address='', phone_number='')
            
        p_form = CustomerProfileForm(request.POST, instance=request.user.customer_profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, _('Your account has been updated!'))
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        # Ensure customer profile exists
        if not hasattr(request.user, 'customer_profile'):
            CustomerProfile.objects.create(user=request.user, address='', phone_number='')
            
        p_form = CustomerProfileForm(instance=request.user.customer_profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'core/profile.html', context)