
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from products.models import Product
import uuid


class Cart(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['session_key']),
        ]

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.username}"
        return f"Guest Cart {self.id}"

    @property
    def total_items(self):
        
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        
        return sum(item.total_price for item in self.items.all())

    def merge_with_user_cart(self, user):
        
        user_cart, created = Cart.objects.get_or_create(user=user)
        
        for item in self.items.all():
            if item.product.is_active and item.product.is_in_stock:
                user_item, created = CartItem.objects.get_or_create(
                    cart=user_cart,
                    product=item.product,
                    defaults={'quantity': 0}
                )
                new_quantity = min(
                    user_item.quantity + item.quantity,
                    item.product.stock
                )
                user_item.quantity = new_quantity
                user_item.save()
        
        self.delete()
        return user_cart


class CartItem(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(99)
        ]
    )
    
    price_at_addition = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cart', 'product']

    def save(self, *args, **kwargs):
        if self.quantity > self.product.stock:
            self.quantity = self.product.stock
        
        if not self.price_at_addition:
            self.price_at_addition = self.product.final_price
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        
        return self.product.final_price * self.quantity

    @property
    def is_available(self):
        
        return (
            self.product.is_active and 
            self.product.is_in_stock and 
            self.quantity <= self.product.stock
        )


class Wishlist(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlists'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='wishlisted_by'
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

