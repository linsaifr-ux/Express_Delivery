import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'express_delivery.settings')
django.setup()

from core.models import ServiceType

def update_service_names():
    print("Updating ServiceType names...")
    
    # Mapping of DeliverySpeed/Old Name to New Chinese Name
    # We can use the DeliverySpeed choices to find the correct Chinese label, 
    # but since we want to update the 'name' field which might be arbitrary,
    # let's try to map based on the delivery_speed field we just added/populated.
    
    # However, existing records might have default 'STANDARD' speed if I didn't migrate data carefully.
    # Let's check what we have.
    
    # Strategy: Update based on existing English name if possible, or fallback to delivery_speed label.
    
    mapping = {
        'Overnight': '隔夜送達',
        '2-Day Delivery': '兩日送達',
        'Standard Express': '標準快遞',
        'Economy Express': '經濟快遞',
        'Test Overnight': '測試隔夜送達', # For the test record I created
        'Standard Service': '標準服務', # For test record
        'Overnight Service': '隔夜服務', # For test record
    }

    for service in ServiceType.objects.all():
        old_name = service.name
        new_name = mapping.get(old_name)
        
        if not new_name:
            # Try to use the label from delivery_speed choice
            new_name = service.get_delivery_speed_display()
            
        if new_name and new_name != old_name:
            service.name = new_name
            service.save()
            print(f"Updated '{old_name}' to '{new_name}'")
        else:
            print(f"Skipped '{old_name}' (No mapping or already correct)")

if __name__ == '__main__':
    update_service_names()
