import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'express_delivery.settings')
django.setup()

from core.models import ServiceType

print("Listing all ServiceType objects:")
for service in ServiceType.objects.all():
    print(f"ID: {service.id}, Name: '{service.name}', Speed: {service.delivery_speed}, Price: {service.base_price}")
