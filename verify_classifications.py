import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'express_delivery.settings')
django.setup()

from core.models import ServiceType, Package, User

def verify_classifications():
    print("Verifying ServiceType classifications...")
    # Check ServiceType choices
    expected_speeds = ['OVERNIGHT', 'TWO_DAY', 'STANDARD', 'ECONOMY']
    actual_speeds = [choice[0] for choice in ServiceType.DeliverySpeed.choices]
    
    missing_speeds = set(expected_speeds) - set(actual_speeds)
    if missing_speeds:
        print(f"FAIL: Missing Delivery Speeds: {missing_speeds}")
    else:
        print("PASS: All Delivery Speeds present.")

    print("\nVerifying Package classifications...")
    # Check Package choices
    expected_types = ['FLAT_ENVELOPE', 'SMALL_BOX', 'MEDIUM_BOX', 'LARGE_BOX']
    actual_types = [choice[0] for choice in Package.PackageType.choices]
    
    missing_types = set(expected_types) - set(actual_types)
    if missing_types:
        print(f"FAIL: Missing Package Types: {missing_types}")
    else:
        print("PASS: All Package Types present.")

    # Create instances to verify DB persistence
    print("\nTesting DB persistence...")
    try:
        service = ServiceType.objects.create(
            name="Test Overnight",
            base_price=100,
            weight_factor=10,
            delivery_speed=ServiceType.DeliverySpeed.OVERNIGHT
        )
        print(f"Created ServiceType: {service.name} with speed {service.delivery_speed}")
        
        user, _ = User.objects.get_or_create(username="test_user_class")

        pkg = Package.objects.create(
            sender=user,
            receiver_name="Test Receiver",
            receiver_address="123 Test St",
            receiver_phone="1234567890",
            weight=2.5,
            dimensions="10x10x10",
            service_type=service,
            package_type=Package.PackageType.LARGE_BOX
        )
        print(f"Created Package: {pkg.tracking_number} with type {pkg.package_type}")
        
        # Clean up
        pkg.delete()
        service.delete()
        print("PASS: DB persistence verified.")
        
    except Exception as e:
        print(f"FAIL: DB persistence failed: {e}")

if __name__ == '__main__':
    verify_classifications()
