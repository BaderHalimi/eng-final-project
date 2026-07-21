"""
Products Models - SECURE VERSION
أمان: جميع الحقول محمية ومُتحقق منها
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from decimal import Decimal
import uuid
import os

User = get_user_model()


def secure_image_path(instance, filename):
    """
    أمان: إنشاء مسار آمن للصور مع اسم عشوائي
    يمنع: Path Traversal, Malicious File Upload
    """
    ext = filename.split('.')[-1].lower()

    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    if ext not in allowed_extensions:
        ext = 'jpg'
    filename = f'{uuid.uuid4().hex}.{ext}'
    return os.path.join('products', filename)


class Category(models.Model):
    """تصنيفات المنتجات"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=secure_image_path, blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    """المنتجات"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )
    

    stock = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(999999)]
    )
    
    image = models.ImageField(upload_to=secure_image_path, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'is_featured']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

            counter = 1
            original_slug = self.slug
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        """السعر النهائي بعد الخصم"""
        if self.discount_price and self.discount_price < self.price:
            return self.discount_price
        return self.price

    @property
    def is_in_stock(self):
        return self.stock > 0


class ProductImage(models.Model):
    """صور إضافية للمنتج"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to=secure_image_path)
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.product.name}"


class Review(models.Model):
    """تقييمات المنتجات"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=100)
    comment = models.TextField(max_length=1000)
    
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:

        unique_together = ['product', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"
