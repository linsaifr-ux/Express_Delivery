import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'express_delivery.settings')
django.setup()

from core.models import User, CustomerProfile, Package
from core.forms import PackageForm

def verify_payment_methods():
    # Clean up existing test users
    User.objects.filter(username__startswith='test_pay_').delete()

    # Define test cases
    test_cases = [
        {
            'username': 'test_pay_contract',
            'type': CustomerProfile.CustomerType.CONTRACT,
            'expected': ['MONTHLY']
        },
        {
            'username': 'test_pay_non_contract',
            'type': CustomerProfile.CustomerType.NON_CONTRACT,
            'expected': ['CASH', 'CREDIT_CARD']
        },
        {
            'username': 'test_pay_prepaid',
            'type': CustomerProfile.CustomerType.PREPAID,
            'expected': ['PREPAID']
        }
    ]

    for case in test_cases:
        print(f"\nTesting {case['type']}...")
        user = User.objects.create_user(username=case['username'], password='password')
        CustomerProfile.objects.create(
            user=user,
            customer_type=case['type'],
            address='Addr',
            phone_number='123'
        )
        
        form = PackageForm(user=user)
        choices = [c[0] for c in form.fields['payment_method'].choices]
        
        print(f"Available choices: {choices}")
        
        if set(choices) == set(case['expected']):
            print("  Choices check: PASS")
        else:
            print(f"  Choices check: FAIL: Expected {case['expected']}, got {choices}")

        # Test form validation
        from core.models import ServiceType
        service = ServiceType.objects.first()
        if not service:
            service = ServiceType.objects.create(name='Standard', base_price=10, weight_factor=1)

        # 1. Test valid payment method
        valid_method = case['expected'][0]
        data = {
            'receiver_name': 'Receiver',
            'receiver_address': 'Address',
            'receiver_phone': '1234567890',
            'weight': 1.0,
            'dimensions': '10x10x10',
            'service_type': service.id,
            'payment_method': valid_method,
            'is_fragile': False,
            'is_hazardous': False
        }
        form = PackageForm(data=data, user=user)
        if form.is_valid():
            print(f"  Validation with {valid_method}: PASS")
        else:
            print(f"  Validation with {valid_method}: FAIL - {form.errors}")

        # 2. Test invalid payment method (if any exist)
        all_methods = ['MONTHLY', 'CASH', 'CREDIT_CARD', 'PREPAID']
        invalid_methods = [m for m in all_methods if m not in case['expected']]
        
        if invalid_methods:
            invalid_method = invalid_methods[0]
            data['payment_method'] = invalid_method
            form = PackageForm(data=data, user=user)
            if not form.is_valid() and 'payment_method' in form.errors:
                print(f"  Rejection of {invalid_method}: PASS")
            else:
                print(f"  Rejection of {invalid_method}: FAIL - Form should be invalid")
        else:
            print("  No invalid methods to test")

if __name__ == '__main__':
    verify_payment_methods()
