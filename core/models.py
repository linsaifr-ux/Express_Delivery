from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        STAFF = 'STAFF', _('Staff')
        DRIVER = 'DRIVER', _('Driver')
        CUSTOMER = 'CUSTOMER', _('Customer')

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER, verbose_name=_('Role'))

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

class CustomerProfile(models.Model):
    class CustomerType(models.TextChoices):
        CONTRACT = 'CONTRACT', _('Contract Customer (Monthly Account)')
        NON_CONTRACT = 'NON_CONTRACT', _('Non-Contract Customer (Cash/Credit Card)')
        PREPAID = 'PREPAID', _('Prepaid Customer (Merchant/Third Party)')

    class BillingPreference(models.TextChoices):
        MONTHLY = 'MONTHLY', _('Monthly Billing')
        COD = 'COD', _('Cash on Delivery')
        CASH = 'CASH', _('Cash Payment')
        CREDIT_CARD = 'CREDIT_CARD', _('Credit Card Payment')
        PREPAID = 'PREPAID', _('Prepaid')

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile', verbose_name=_('User'))
    customer_type = models.CharField(max_length=20, choices=CustomerType.choices, default=CustomerType.NON_CONTRACT, verbose_name=_('Customer Type'))
    billing_preference = models.CharField(max_length=20, choices=BillingPreference.choices, default=BillingPreference.CASH, verbose_name=_('Billing Preference'))
    address = models.TextField(verbose_name=_('Address'))
    phone_number = models.CharField(max_length=20, verbose_name=_('Phone Number'))

    class Meta:
        verbose_name = _('Customer Profile')
        verbose_name_plural = _('Customer Profiles')

    def __str__(self):
        return f"{self.user.username} ({self.customer_type})"

class ServiceType(models.Model):
    class DeliverySpeed(models.TextChoices):
        OVERNIGHT = 'OVERNIGHT', _('Overnight Delivery')
        TWO_DAY = 'TWO_DAY', _('Two-Day Delivery')
        STANDARD = 'STANDARD', _('Standard Delivery')
        ECONOMY = 'ECONOMY', _('Economy Delivery')

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Service Name'))
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Base Price'))
    weight_factor = models.DecimalField(max_digits=5, decimal_places=2, help_text=_("Price per kg"), verbose_name=_('Weight Factor'))
    speed_factor = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, help_text=_("Speed Multiplier"), verbose_name=_('Speed Factor'))
    delivery_speed = models.CharField(max_length=20, choices=DeliverySpeed.choices, default=DeliverySpeed.STANDARD, verbose_name=_('Delivery Speed'))
    description = models.TextField(blank=True, verbose_name=_('Description'))

    class Meta:
        verbose_name = _('Service Type')
        verbose_name_plural = _('Service Types')

    def __str__(self):
        return self.name

class Package(models.Model):
    class Status(models.TextChoices):
        CREATED = 'CREATED', _('Created')
        PICKED_UP = 'PICKED_UP', _('Picked Up')
        IN_TRANSIT = 'IN_TRANSIT', _('In Transit')
        SORTING = 'SORTING', _('Sorting')
        HUB_TRANSFER = 'HUB_TRANSFER', _('Hub Transfer')
        OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY', _('Out for Delivery')
        DELIVERED = 'DELIVERED', _('Delivered')
        EXCEPTION = 'EXCEPTION', _('Exception')

    class PackageType(models.TextChoices):
        FLAT_ENVELOPE = 'FLAT_ENVELOPE', _('Flat Envelope')
        SMALL_BOX = 'SMALL_BOX', _('Small Box')
        MEDIUM_BOX = 'MEDIUM_BOX', _('Medium Box')
        LARGE_BOX = 'LARGE_BOX', _('Large Box')

    tracking_number = models.CharField(max_length=50, unique=True, editable=False, verbose_name=_('Tracking Number'))
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_packages', verbose_name=_('Sender'))
    receiver_name = models.CharField(max_length=100, verbose_name=_('Receiver Name'))
    receiver_address = models.TextField(verbose_name=_('Receiver Address'))
    receiver_phone = models.CharField(max_length=20, verbose_name=_('Receiver Phone'))
    
    weight = models.DecimalField(max_digits=6, decimal_places=2, help_text=_("Weight (kg)"), verbose_name=_('Weight'))
    dimensions = models.CharField(max_length=100, help_text=_("LxWxH (cm)"), verbose_name=_('Dimensions'))
    declared_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_('Declared Value'))
    description = models.TextField(blank=True, verbose_name=_('Description of Contents'))
    package_type = models.CharField(max_length=20, choices=PackageType.choices, default=PackageType.SMALL_BOX, verbose_name=_('Package Type'))
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT, verbose_name=_('Service Type'))
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED, verbose_name=_('Status'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    estimated_delivery = models.DateTimeField(null=True, blank=True, verbose_name=_('Estimated Delivery'))
    
    # Billing
    class PaymentMethod(models.TextChoices):
        MONTHLY = 'MONTHLY', _('Monthly Billing')
        CASH = 'CASH', _('Cash Payment')
        CREDIT_CARD = 'CREDIT_CARD', _('Credit Card Payment')
        PREPAID = 'PREPAID', _('Prepaid (Merchant/Third Party)')

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_('Price'))
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH, verbose_name=_('Payment Method'))
    
    # Special handling
    is_fragile = models.BooleanField(default=False, verbose_name=_('Fragile'))
    is_hazardous = models.BooleanField(default=False, verbose_name=_('Hazardous'))

    # Proof of Delivery
    signature = models.ImageField(upload_to='signatures/', blank=True, null=True, verbose_name=_('Signature'))
    signed_by = models.CharField(max_length=100, blank=True, verbose_name=_('Signed By'))

    class Meta:
        verbose_name = _('Package')
        verbose_name_plural = _('Packages')

    def calculate_price(self):
        from decimal import Decimal
        base = self.service_type.base_price
        weight_cost = self.service_type.weight_factor * Decimal(str(self.weight))
        # Simple distance simulation or flat rate for now
        total = base + weight_cost
        
        if self.is_fragile:
            total += Decimal('5.00')
        if self.is_hazardous:
            total += Decimal('15.00')
            
        return total

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = str(uuid.uuid4()).replace('-', '').upper()[:12]
        
        if not self.price and self.service_type:
            self.price = self.calculate_price()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tracking_number} - {self.status}"

class TrackingEvent(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='events', verbose_name=_('Package'))
    status = models.CharField(max_length=20, choices=Package.Status.choices, verbose_name=_('Status'))
    location = models.CharField(max_length=200, verbose_name=_('Location'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Timestamp'))

    class Meta:
        verbose_name = _('Tracking Event')
        verbose_name_plural = _('Tracking Events')

    def __str__(self):
        return f"{self.package.tracking_number} - {self.status} at {self.timestamp}"

class Invoice(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PAID = 'PAID', _('Paid')
        OVERDUE = 'OVERDUE', _('Overdue')

    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='invoices', verbose_name=_('Customer'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name=_('Status'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    due_date = models.DateField(verbose_name=_('Due Date'))
    period_start = models.DateField(null=True, blank=True, verbose_name=_('Period Start'))
    period_end = models.DateField(null=True, blank=True, verbose_name=_('Period End'))

    class Meta:
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')

    def __str__(self):
        return f"Invoice #{self.id} - {self.customer.user.username} - {self.amount}"
