import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import django
from django.db.models import Count

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'express_delivery.settings')
django.setup()

from core.models import ServiceType, Package

def fix_duplicates():
    print("Starting service type cleanup...")
    
    # Find names with duplicates
    duplicates = ServiceType.objects.values('name').annotate(count=Count('id')).filter(count__gt=1)
    
    for entry in duplicates:
        name = entry['name']
        print(f"\nProcessing duplicates for: {name}")
        
        services = list(ServiceType.objects.filter(name=name).order_by('id'))
        
        # Keep the first one (lowest ID)
        primary = services[0]
        to_delete = services[1:]
        
        print(f"Keeping primary: ID {primary.id} (Price: {primary.base_price})")
        
        for service in to_delete:
            print(f"  Merging ID {service.id} (Price: {service.base_price}) into ID {primary.id}")
            
            # Update packages
            packages = Package.objects.filter(service_type=service)
            count = packages.count()
            if count > 0:
                print(f"    Updating {count} packages...")
                packages.update(service_type=primary)
            
            # Delete the duplicate
            print(f"    Deleting ID {service.id}")
            service.delete()
            
    print("\nCleanup complete.")

if __name__ == '__main__':
    fix_duplicates()
