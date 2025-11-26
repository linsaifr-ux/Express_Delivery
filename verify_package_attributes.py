
import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'express_delivery.settings')
django.setup()

from core.models import Package, User, ServiceType

def verify_package_attributes():
    # Ensure we have a user and service type
    user, _ = User.objects.get_or_create(username='testuser_pkg_attr', email='test@example.com')
    service_type, _ = ServiceType.objects.get_or_create(
        name='Standard Test', 
        defaults={
            'base_price': Decimal('10.00'), 
            'weight_factor': Decimal('2.00'), 
            'speed_factor': Decimal('1.00')
        }
    )

    # Create a package with new attributes
    package = Package.objects.create(
        sender=user,
        receiver_name='Receiver',
        receiver_address='123 Main St',
        receiver_phone='555-1234',
        weight=Decimal('5.00'),
        dimensions='10x10x10',
        declared_value=Decimal('100.00'),
        description='Test Contents',
        service_type=service_type
    )

    # Verify attributes
    print(f"Package Created: {package.tracking_number}")
    print(f"Weight: {package.weight}")
    print(f"Dimensions: {package.dimensions}")
    print(f"Declared Value: {package.declared_value}")
    print(f"Description: {package.description}")

    assert package.weight == Decimal('5.00')
    assert package.dimensions == '10x10x10'
    assert package.declared_value == Decimal('100.00')
    assert package.description == 'Test Contents'
    
    print("Verification Successful!")

if __name__ == '__main__':
    verify_package_attributes()
