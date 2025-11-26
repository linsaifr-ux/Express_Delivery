from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User, Package, CustomerProfile

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label=_('Email'))

    class Meta:
        model = User
        fields = ['email']

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['address', 'phone_number']
        labels = {
            'address': _('Address'),
            'phone_number': _('Phone Number'),
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class CustomUserCreationForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['receiver_name', 'receiver_address', 'receiver_phone', 'weight', 'dimensions', 'package_type', 'service_type', 'payment_method', 'is_fragile', 'is_hazardous']
        widgets = {
            'receiver_address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and hasattr(user, 'customer_profile'):
            customer_type = user.customer_profile.customer_type
            from .models import CustomerProfile, Package
            
            allowed_methods = []
            if customer_type == CustomerProfile.CustomerType.CONTRACT:
                allowed_methods = [Package.PaymentMethod.MONTHLY]
            elif customer_type == CustomerProfile.CustomerType.NON_CONTRACT:
                allowed_methods = [Package.PaymentMethod.CASH, Package.PaymentMethod.CREDIT_CARD]
            elif customer_type == CustomerProfile.CustomerType.PREPAID:
                allowed_methods = [Package.PaymentMethod.PREPAID]
                
            self.fields['payment_method'].choices = [
                (choice[0], choice[1]) 
                for choice in Package.PaymentMethod.choices 
                if choice[0] in allowed_methods
            ]
