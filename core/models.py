from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('管理員')
        STAFF = 'STAFF', _('員工')
        DRIVER = 'DRIVER', _('司機')
        CUSTOMER = 'CUSTOMER', _('客戶')

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER, verbose_name=_('角色'))

    class Meta:
        verbose_name = _('使用者')
        verbose_name_plural = _('使用者')

class CustomerProfile(models.Model):
    class CustomerType(models.TextChoices):
        CONTRACT = 'CONTRACT', _('合約客戶 (設有月結帳戶)')
        NON_CONTRACT = 'NON_CONTRACT', _('非合約客戶 (以現金或信用卡支付)')
        PREPAID = 'PREPAID', _('預付客戶 (貨運費用由商家或第三方支付)')

    class BillingPreference(models.TextChoices):
        MONTHLY = 'MONTHLY', _('月結帳單')
        COD = 'COD', _('貨到付款')
        CASH = 'CASH', _('現金支付')
        CREDIT_CARD = 'CREDIT_CARD', _('信用卡支付')
        PREPAID = 'PREPAID', _('預付')

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile', verbose_name=_('使用者'))
    customer_type = models.CharField(max_length=20, choices=CustomerType.choices, default=CustomerType.NON_CONTRACT, verbose_name=_('客戶類型'))
    billing_preference = models.CharField(max_length=20, choices=BillingPreference.choices, default=BillingPreference.CASH, verbose_name=_('帳單偏好'))
    address = models.TextField(verbose_name=_('地址'))
    phone_number = models.CharField(max_length=20, verbose_name=_('電話號碼'))

    class Meta:
        verbose_name = _('客戶資料')
        verbose_name_plural = _('客戶資料')

    def __str__(self):
        return f"{self.user.username} ({self.customer_type})"

class ServiceType(models.Model):
    class DeliverySpeed(models.TextChoices):
        OVERNIGHT = 'OVERNIGHT', _('隔夜送達')
        TWO_DAY = 'TWO_DAY', _('兩日送達')
        STANDARD = 'STANDARD', _('標準快遞')
        ECONOMY = 'ECONOMY', _('經濟快遞')

    name = models.CharField(max_length=100, verbose_name=_('服務名稱'))
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('基本價格'))
    weight_factor = models.DecimalField(max_digits=5, decimal_places=2, help_text=_("每公斤價格"), verbose_name=_('重量係數'))
    speed_factor = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, help_text=_("速度倍率"), verbose_name=_('速度係數'))
    delivery_speed = models.CharField(max_length=20, choices=DeliverySpeed.choices, default=DeliverySpeed.STANDARD, verbose_name=_('配送速度'))
    description = models.TextField(blank=True, verbose_name=_('描述'))

    class Meta:
        verbose_name = _('服務類型')
        verbose_name_plural = _('服務類型')

    def __str__(self):
        return self.name

class Package(models.Model):
    class Status(models.TextChoices):
        CREATED = 'CREATED', _('已建立')
        PICKED_UP = 'PICKED_UP', _('已取件')
        IN_TRANSIT = 'IN_TRANSIT', _('運送中')
        OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY', _('配送中')
        DELIVERED = 'DELIVERED', _('已送達')
        EXCEPTION = 'EXCEPTION', _('異常')

    class PackageType(models.TextChoices):
        FLAT_ENVELOPE = 'FLAT_ENVELOPE', _('扁平信封')
        SMALL_BOX = 'SMALL_BOX', _('小型箱')
        MEDIUM_BOX = 'MEDIUM_BOX', _('中型箱')
        LARGE_BOX = 'LARGE_BOX', _('大型箱')

    tracking_number = models.CharField(max_length=50, unique=True, editable=False, verbose_name=_('追蹤號碼'))
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_packages', verbose_name=_('寄件人'))
    receiver_name = models.CharField(max_length=100, verbose_name=_('收件人姓名'))
    receiver_address = models.TextField(verbose_name=_('收件人地址'))
    receiver_phone = models.CharField(max_length=20, verbose_name=_('收件人電話'))
    
    weight = models.DecimalField(max_digits=6, decimal_places=2, help_text=_("重量 (公斤)"), verbose_name=_('重量'))
    dimensions = models.CharField(max_length=100, help_text=_("長x寬x高 (公分)"), verbose_name=_('尺寸'))
    package_type = models.CharField(max_length=20, choices=PackageType.choices, default=PackageType.SMALL_BOX, verbose_name=_('包裹類型'))
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT, verbose_name=_('服務類型'))
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED, verbose_name=_('狀態'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('建立時間'))
    estimated_delivery = models.DateTimeField(null=True, blank=True, verbose_name=_('預計送達時間'))
    
    # Billing
    class PaymentMethod(models.TextChoices):
        MONTHLY = 'MONTHLY', _('月結帳單')
        CASH = 'CASH', _('現金支付')
        CREDIT_CARD = 'CREDIT_CARD', _('信用卡支付')
        PREPAID = 'PREPAID', _('預付 (由商家/第三方支付)')

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_('價格'))
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH, verbose_name=_('付款方式'))
    
    # Special handling
    is_fragile = models.BooleanField(default=False, verbose_name=_('易碎品'))
    is_hazardous = models.BooleanField(default=False, verbose_name=_('危險物品'))

    class Meta:
        verbose_name = _('包裹')
        verbose_name_plural = _('包裹')

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
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='events', verbose_name=_('包裹'))
    status = models.CharField(max_length=20, choices=Package.Status.choices, verbose_name=_('狀態'))
    location = models.CharField(max_length=200, verbose_name=_('地點'))
    description = models.TextField(blank=True, verbose_name=_('描述'))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('時間'))

    class Meta:
        verbose_name = _('追蹤事件')
        verbose_name_plural = _('追蹤事件')

    def __str__(self):
        return f"{self.package.tracking_number} - {self.status} at {self.timestamp}"

class Invoice(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('待付款')
        PAID = 'PAID', _('已付款')
        OVERDUE = 'OVERDUE', _('逾期')

    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='invoices', verbose_name=_('客戶'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('金額'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name=_('狀態'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('建立時間'))
    due_date = models.DateField(verbose_name=_('到期日'))
    period_start = models.DateField(null=True, blank=True, verbose_name=_('計費週期開始'))
    period_end = models.DateField(null=True, blank=True, verbose_name=_('計費週期結束'))

    class Meta:
        verbose_name = _('帳單')
        verbose_name_plural = _('帳單')

    def __str__(self):
        return f"Invoice #{self.id} - {self.customer.user.username} - {self.amount}"
