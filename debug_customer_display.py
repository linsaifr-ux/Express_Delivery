import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'express_delivery.settings')
django.setup()

from core.models import User, CustomerProfile

def debug_display():
    # Create a test user
    username = 'debug_display_user'
    User.objects.filter(username=username).delete()
    user = User.objects.create_user(username=username, password='password')
    
    # Create profile (default is NON_CONTRACT)
    profile = CustomerProfile.objects.create(user=user, address='Addr', phone_number='123')
    
    print(f"Type: {profile.customer_type}")
    print(f"Display: {profile.get_customer_type_display()}")
    
    # Change to CONTRACT
    profile.customer_type = CustomerProfile.CustomerType.CONTRACT
    profile.save()
    print(f"Type: {profile.customer_type}")
    print(f"Display: {profile.get_customer_type_display()}")

if __name__ == '__main__':
    debug_display()
