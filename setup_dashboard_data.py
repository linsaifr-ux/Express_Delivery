import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'express_delivery.settings')
django.setup()

from core.models import User, Package, ServiceType, CustomerProfile

def setup_test_data():
    username = 'test_dashboard_user'
    password = 'password'
    email = 'dashboard@example.com'
    
    # Create or get user
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    if created:
        user.set_password(password)
        user.save()
        CustomerProfile.objects.create(user=user, address='Test Addr', phone_number='123')
        print(f"Created user: {username}")
    else:
        print(f"User {username} already exists")
        
    # Create service type if needed
    service_type, _ = ServiceType.objects.get_or_create(
        name='Standard',
        defaults={
            'base_price': 100,
            'weight_factor': 10,
            'speed_factor': 1.0,
            'description': 'Standard delivery'
        }
    )
    
    # Create package
    package, created = Package.objects.get_or_create(
        tracking_number='TRACK123',
        defaults={
            'sender': user,
            'receiver_name': 'Receiver',
            'receiver_address': 'Addr',
            'receiver_phone': '123',
            'weight': 1.0,
            'service_type': service_type,
            'status': 'created',
            'created_at': timezone.now()
        }
    )
    if created:
        print(f"Created package: {package.tracking_number}")
    else:
        print(f"Package {package.tracking_number} already exists")

if __name__ == '__main__':
    setup_test_data()
