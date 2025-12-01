import os
import django
from decimal import Decimal
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'express_delivery.settings')
django.setup()

from core.models import User, Package, ServiceType, TrackingEvent
from django.core.files.uploadedfile import SimpleUploadedFile

def verify_tracking():
    with open('verification_result.txt', 'w') as f:
        def log(msg):
            print(msg)
            f.write(msg + '\n')

        log("Verifying Tracking Lifecycle...")
        
        # Setup
        user_name = 'tracking_test_user_2'
        if not User.objects.filter(username=user_name).exists():
            user = User.objects.create_user(username=user_name, password='password123')
        else:
            user = User.objects.get(username=user_name)
            
        service_name = 'Tracking Test Service'
        if not ServiceType.objects.filter(name=service_name).exists():
            service = ServiceType.objects.create(
                name=service_name,
                base_price=Decimal('10.00'),
                weight_factor=Decimal('1.00')
            )
        else:
            service = ServiceType.objects.get(name=service_name)

        # Create Package
        log("Creating Package...")
        package = Package.objects.create(
            sender=user,
            receiver_name='Receiver',
            receiver_address='Address',
            receiver_phone='1234567890',
            weight=Decimal('1.0'),
            service_type=service
        )
        
        log(f"Package created: {package.tracking_number}")
        
        # Verify CREATED event
        events = TrackingEvent.objects.filter(package=package).order_by('timestamp')
        if events.exists() and events.first().status == Package.Status.CREATED:
            log("PASS: Initial CREATED event found.")
        else:
            log("FAIL: Initial CREATED event not found.")
            
        # Update Statuses
        statuses_to_test = [
            Package.Status.PICKED_UP,
            Package.Status.SORTING,
            Package.Status.HUB_TRANSFER,
            Package.Status.OUT_FOR_DELIVERY,
            Package.Status.DELIVERED
        ]
        
        for status in statuses_to_test:
            log(f"Updating status to {status}...")
            package.status = status
            package.save()
            
            # Verify event
            latest_event = TrackingEvent.objects.filter(package=package).order_by('-timestamp').first()
            if latest_event and latest_event.status == status:
                log(f"PASS: Event for {status} created.")
            else:
                log(f"FAIL: Event for {status} NOT created.")

        # Verify Signature
        log("Verifying Signature...")
        package.signed_by = 'Receiver Name'
        # Create a dummy image
        dummy_image = SimpleUploadedFile(name='test_sig.jpg', content=b'fake_image_content', content_type='image/jpeg')
        package.signature = dummy_image
        package.save()
        
        package.refresh_from_db()
        if package.signed_by == 'Receiver Name' and package.signature:
            log("PASS: Signature fields saved.")
        else:
            log("FAIL: Signature fields not saved.")

if __name__ == '__main__':
    verify_tracking()
