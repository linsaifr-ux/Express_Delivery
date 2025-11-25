import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'express_delivery.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from core.models import User, CustomerProfile
from core.views import profile
from core.forms import UserUpdateForm, CustomerProfileForm

def verify_profile_update():
    # Setup user
    username = 'test_profile_user'
    User.objects.filter(username=username).delete()
    user = User.objects.create_user(username=username, password='password', email='old@example.com')
    CustomerProfile.objects.create(user=user, address='Old Addr', phone_number='111')

    print(f"Initial: Email={user.email}, Address={user.customer_profile.address}")

    # Simulate POST request
    factory = RequestFactory()
    data = {
        'email': 'new@example.com',
        'address': 'New Addr',
        'phone_number': '222'
    }
    request = factory.post('/profile/', data)
    request.user = user
    
    # Add message support
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)

    response = profile(request)

    # Refresh from db
    user.refresh_from_db()
    
    print(f"Updated: Email={user.email}, Address={user.customer_profile.address}")

    if user.email == 'new@example.com' and user.customer_profile.address == 'New Addr':
        print("PASS: Profile updated successfully")
    else:
        print("FAIL: Profile not updated correctly")

if __name__ == '__main__':
    verify_profile_update()
