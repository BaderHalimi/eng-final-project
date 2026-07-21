
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from products.models import Product
from accounts.models import Address
from decimal import Decimal
import uuid
import hashlib
import json


class Order(models.Model):
    
    ORDER_STATUS = (
        ('pending', 'قيد الانتظار'),
        ('confirmed', 'مؤكد'),
        ('processing', 'قيد المعالجة'),
        ('shipped', 'تم الشحن'),
        ('delivered', 'تم التوصيل'),
        ('cancelled', 'ملغي'),
        ('refunded', 'مسترد'),
    )
    
    PAYMENT_STATUS = (
        ('pending', 'قيد الانتظار'),
        ('paid', 'مدفوع'),
        ('failed', 'فشل'),
        ('refunded', 'مسترد'),
    )
    
    PAYMENT_METHODS = (
        ('cod', 'الدفع عند الاستلام'),
        ('credit_card', 'بطاقة ائتمان'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'تحويل بنكي'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )
    
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    integrity_hash = models.CharField(max_length=64, editable=False)
    
    shipping_address = models.JSONField()
    billing_address = models.JSONField()
    
    notes = models.TextField(blank=True, max_length=500)
    
    tracking_number = models.CharField(max_length=100, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.order_number:
            import time
            self.order_number = f"ORD-{int(time.time())}-{uuid.uuid4().hex[:6].upper()}"
        
        self.integrity_hash = self._calculate_integrity_hash()
        
        super().save(*args, **kwargs)

    def _calculate_integrity_hash(self):
        
        data = {
            'subtotal': str(self.subtotal),
            'tax': str(self.tax),
            'shipping_cost': str(self.shipping_cost),
            'discount': str(self.discount),
            'total': str(self.total),
            'order_number': self.order_number or '',
        }
        data_str = json.dumps(data, sort_keys=True)
        secret = getattr(settings, 'SECRET_KEY', 'default-secret')
        return hashlib.sha256(f"{data_str}{secret}".encode()).hexdigest()

    def verify_integrity(self):
        
        return self.integrity_hash == self._calculate_integrity_hash()

    def __str__(self):
        return f"Order {self.order_number}"

    @property
    def can_cancel(self):
        
        return self.status in ['pending', 'confirmed']


class OrderItem(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items'
    )
    
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=50, blank=True)
    
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)]
    )
    
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"


class Coupon(models.Model):
    
    DISCOUNT_TYPES = (
        ('percentage', 'نسبة مئوية'),
        ('fixed', 'مبلغ ثابت'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    minimum_order = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    maximum_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    usage_limit_per_user = models.PositiveIntegerField(default=1)
    times_used = models.PositiveIntegerField(default=0)
    
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    def is_valid(self):
        
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.usage_limit and self.times_used >= self.usage_limit:
            return False
        
        return True

    def calculate_discount(self, subtotal):
        
        if subtotal < self.minimum_order:
            return Decimal('0.00')
        
        if self.discount_type == 'percentage':
            discount = subtotal * (self.discount_value / 100)
            if self.maximum_discount:
                discount = min(discount, self.maximum_discount)
        else:
            discount = self.discount_value
        
        return min(discount, subtotal)


class CouponUsage(models.Model):
    
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name='usages'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coupon_usages'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='coupon_usage'
    )
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-used_at']

    def __str__(self):
        return f"{self.user.username} used {self.coupon.code}"

