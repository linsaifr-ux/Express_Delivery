from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import CustomerProfile, Invoice, Package
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generates monthly invoices for contract customers'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        # For simplicity, let's just invoice everything up to now that isn't invoiced
        # In a real system, you'd filter by date range (e.g., last month)
        
        contract_customers = CustomerProfile.objects.filter(customer_type=CustomerProfile.CustomerType.CONTRACT)
        
        count = 0
        for customer in contract_customers:
            # Find packages sent by this customer that are not associated with an invoice (logic simplified)
            # In a real app, we'd need a ManyToMany or ForeignKey from Invoice to Package, 
            # or mark packages as 'invoiced'. For now, let's assume we just calculate total.
            
            packages = Package.objects.filter(sender=customer.user, created_at__lte=now)
            
            # This is a simplification. Real system needs to track which packages are on which invoice.
            # Let's just create a dummy invoice for demonstration.
            
            total_amount = sum(pkg.price for pkg in packages)
            
            if total_amount > 0:
                Invoice.objects.create(
                    customer=customer,
                    amount=total_amount,
                    due_date=now.date() + timedelta(days=30),
                    period_end=now.date()
                )
                count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Generated {count} invoices'))
