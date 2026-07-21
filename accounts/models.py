
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid
import secrets


class CustomUser(AbstractUser):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="رقم الهاتف يجب أن يكون بالصيغة: '+999999999'. حتى 15 رقم مسموح."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=64, blank=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    
    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    lockout_until = models.DateTimeField(null=True, blank=True)
    
    password_changed_at = models.DateTimeField(null=True, blank=True)
    
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    def generate_email_verification_token(self):
        
        self.email_verification_token = secrets.token_urlsafe(48)
        self.email_verification_sent_at = timezone.now()
        self.save(update_fields=['email_verification_token', 'email_verification_sent_at'])
        return self.email_verification_token

    def is_locked_out(self):
        
        if self.lockout_until and self.lockout_until > timezone.now():
            return True
        return False

    def record_failed_login(self):
        
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.lockout_until = timezone.now() + timezone.timedelta(minutes=30)
        self.save(update_fields=['failed_login_attempts', 'lockout_until'])

    def reset_failed_logins(self):
        
        self.failed_login_attempts = 0
        self.lockout_until = None
        self.save(update_fields=['failed_login_attempts', 'lockout_until'])


class Address(models.Model):
    
    ADDRESS_TYPES = (
        ('billing', 'عنوان الفواتير'),
        ('shipping', 'عنوان الشحن'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES)
    
    full_name = models.CharField(max_length=100)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    phone = models.CharField(max_length=17, blank=True)
    
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', '-created_at']

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(
                user=self.user, 
                address_type=self.address_type,
                is_default=True
            ).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.city}"


class UserActivity(models.Model):
    
    ACTIVITY_TYPES = (
        ('login', 'تسجيل دخول'),
        ('logout', 'تسجيل خروج'),
        ('failed_login', 'محاولة دخول فاشلة'),
        ('password_change', 'تغيير كلمة المرور'),
        ('password_reset', 'إعادة تعيين كلمة المرور'),
        ('profile_update', 'تحديث الملف الشخصي'),
        ('email_change', 'تغيير البريد الإلكتروني'),
        ('2fa_enabled', 'تفعيل التحقق الثنائي'),
        ('2fa_disabled', 'إلغاء التحقق الثنائي'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='activities',
        null=True,
        blank=True
    )
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'User Activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        username = self.user.username if self.user else 'Unknown'
        return f"{username} - {self.activity_type} - {self.created_at}"

