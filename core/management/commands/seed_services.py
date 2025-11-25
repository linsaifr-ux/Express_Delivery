from django.core.management.base import BaseCommand
from core.models import ServiceType

class Command(BaseCommand):
    help = 'Seeds initial ServiceType data'

    def handle(self, *args, **kwargs):
        services = [
            {
                'name': 'Standard Delivery',
                'base_price': 5.00,
                'weight_factor': 2.00,
                'speed_factor': 1.00,
                'description': '3-5 business days'
            },
            {
                'name': 'Express Delivery',
                'base_price': 10.00,
                'weight_factor': 3.00,
                'speed_factor': 1.50,
                'description': '1-2 business days'
            },
            {
                'name': 'Overnight Delivery',
                'base_price': 20.00,
                'weight_factor': 5.00,
                'speed_factor': 2.00,
                'description': 'Next day delivery'
            }
        ]

        for service_data in services:
            ServiceType.objects.get_or_create(name=service_data['name'], defaults=service_data)
            self.stdout.write(self.style.SUCCESS(f"Created/Updated service: {service_data['name']}"))
