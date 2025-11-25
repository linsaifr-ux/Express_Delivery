import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'express_delivery.settings')
django.setup()

from core.models import User, CustomerProfile

def verify_customer_types():
    # Clean up existing test users
    User.objects.filter(username__startswith='test_').delete()

    # 1. Contract Customer
    user1 = User.objects.create_user(username='test_contract', password='password')
    profile1 = CustomerProfile.objects.create(
        user=user1,
        customer_type=CustomerProfile.CustomerType.CONTRACT,
        billing_preference=CustomerProfile.BillingPreference.MONTHLY,
        address='Addr 1',
        phone_number='123'
    )
    print(f"Created: {profile1.get_customer_type_display()}")

    # 2. Non-contract Customer
    user2 = User.objects.create_user(username='test_non_contract', password='password')
    profile2 = CustomerProfile.objects.create(
        user=user2,
        customer_type=CustomerProfile.CustomerType.NON_CONTRACT,
        billing_preference=CustomerProfile.BillingPreference.CASH,
        address='Addr 2',
        phone_number='456'
    )
    print(f"Created: {profile2.get_customer_type_display()}")

    # 3. Prepaid Customer
    user3 = User.objects.create_user(username='test_prepaid', password='password')
    profile3 = CustomerProfile.objects.create(
        user=user3,
        customer_type=CustomerProfile.CustomerType.PREPAID,
        billing_preference=CustomerProfile.BillingPreference.PREPAID,
        address='Addr 3',
        phone_number='789'
    )
    print(f"Created: {profile3.get_customer_type_display()}")

    # Verify counts
    print(f"Contract Customers: {CustomerProfile.objects.filter(customer_type=CustomerProfile.CustomerType.CONTRACT).count()}")
    print(f"Non-Contract Customers: {CustomerProfile.objects.filter(customer_type=CustomerProfile.CustomerType.NON_CONTRACT).count()}")
    print(f"Prepaid Customers: {CustomerProfile.objects.filter(customer_type=CustomerProfile.CustomerType.PREPAID).count()}")

if __name__ == '__main__':
    verify_customer_types()
