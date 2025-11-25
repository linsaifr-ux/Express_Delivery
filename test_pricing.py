import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'express_delivery.settings')
django.setup()

from core.models import ServiceType, Package, User

def test_pricing():
    print("Testing calculate_price function...")
    
    # Setup
    user, _ = User.objects.get_or_create(username="pricing_test_user")
    
    # Create ServiceTypes with different speeds/factors
    standard_service, _ = ServiceType.objects.get_or_create(
        name="Standard Service",
        defaults={
            'base_price': 100,
            'weight_factor': 10,
            'speed_factor': 1.0,
            'delivery_speed': ServiceType.DeliverySpeed.STANDARD
        }
    )
    
    overnight_service, _ = ServiceType.objects.get_or_create(
        name="Overnight Service",
        defaults={
            'base_price': 200, # Higher base
            'weight_factor': 20, # Higher weight factor
            'speed_factor': 2.0, # Higher speed factor
            'delivery_speed': ServiceType.DeliverySpeed.OVERNIGHT
        }
    )

    # Test Case 1: Standard Package
    pkg1 = Package(
        sender=user,
        weight=2.0,
        service_type=standard_service,
        package_type=Package.PackageType.SMALL_BOX
    )
    price1 = pkg1.calculate_price()
    print(f"Package 1 (Standard, 2kg, Small Box): {price1}")
    # Expected: 100 + (10 * 2) = 120

    # Test Case 2: Overnight Package
    pkg2 = Package(
        sender=user,
        weight=2.0,
        service_type=overnight_service,
        package_type=Package.PackageType.SMALL_BOX
    )
    price2 = pkg2.calculate_price()
    print(f"Package 2 (Overnight, 2kg, Small Box): {price2}")
    # Expected: 200 + (20 * 2) = 240. 
    # Note: Current logic ignores speed_factor in calculation, only uses base_price and weight_factor.
    
    # Test Case 3: Fragile
    pkg3 = Package(
        sender=user,
        weight=2.0,
        service_type=standard_service,
        is_fragile=True
    )
    price3 = pkg3.calculate_price()
    print(f"Package 3 (Standard, 2kg, Fragile): {price3}")
    # Expected: 120 + 5 = 125

    print("\nAnalysis:")
    if price2 > price1:
        print("PASS: Overnight is more expensive (due to base_price/weight_factor differences).")
    else:
        print("FAIL: Overnight is not more expensive.")

if __name__ == '__main__':
    test_pricing()
