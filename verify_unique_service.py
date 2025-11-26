import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import django
from django.db import IntegrityError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'express_delivery.settings')
django.setup()

from core.models import ServiceType

def verify_unique_constraint():
    print("Verifying unique constraint on ServiceType.name...")
    
    # Get an existing service type
    existing = ServiceType.objects.first()
    if not existing:
        print("No existing service types found. Creating one...")
        existing = ServiceType.objects.create(
            name="Test Service",
            base_price=10.00,
            weight_factor=1.00
        )
    
    print(f"Existing service: {existing.name}")
    
    try:
        print("Attempting to create duplicate...")
        ServiceType.objects.create(
            name=existing.name,
            base_price=20.00,
            weight_factor=2.00
        )
        print("FAIL: Duplicate created successfully (Constraint NOT working)")
    except IntegrityError:
        print("PASS: IntegrityError raised (Constraint working)")
    except Exception as e:
        print(f"FAIL: Unexpected error: {e}")

if __name__ == '__main__':
    verify_unique_constraint()
