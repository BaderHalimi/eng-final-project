from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, Coupon, CouponUsage


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'quantity', 'unit_price', 'total_price']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'payment_status', 'total', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'user__email']
    readonly_fields = ['order_number', 'user', 'subtotal', 'tax', 'shipping_cost', 'discount', 
                       'total', 'integrity_hash', 'shipping_address', 'billing_address',
                       'ip_address', 'user_agent', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    ordering = ['-created_at']
    
    fieldsets = (
        ('معلومات الطلب', {
            'fields': ('order_number', 'user', 'status', 'payment_status', 'payment_method')
        }),
        ('المبالغ', {
            'fields': ('subtotal', 'tax', 'shipping_cost', 'discount', 'total', 'integrity_hash')
        }),
        ('العناوين', {
            'fields': ('shipping_address', 'billing_address'),
            'classes': ('collapse',)
        }),
        ('الشحن', {
            'fields': ('tracking_number', 'shipped_at', 'delivered_at')
        }),
        ('معلومات أمنية', {
            'fields': ('ip_address', 'user_agent', 'notes'),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered']
    
    def mark_as_confirmed(self, request, queryset):
        queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, "تم تأكيد الطلبات المحددة")
    mark_as_confirmed.short_description = "تأكيد الطلبات المحددة"
    
    def mark_as_shipped(self, request, queryset):
        queryset.filter(status='confirmed').update(status='shipped')
        self.message_user(request, "تم تحديث حالة الشحن")
    mark_as_shipped.short_description = "تحديث كـ 'تم الشحن'"
    
    def mark_as_delivered(self, request, queryset):
        queryset.filter(status='shipped').update(status='delivered')
        self.message_user(request, "تم تحديث حالة التوصيل")
    mark_as_delivered.short_description = "تحديث كـ 'تم التوصيل'"


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'times_used', 'usage_limit', 'is_active', 'valid_until']
    list_filter = ['is_active', 'discount_type', 'valid_from', 'valid_until']
    search_fields = ['code', 'description']
    list_editable = ['is_active']
    ordering = ['-created_at']
    
    fieldsets = (
        ('معلومات الكوبون', {
            'fields': ('code', 'description')
        }),
        ('الخصم', {
            'fields': ('discount_type', 'discount_value', 'minimum_order', 'maximum_discount')
        }),
        ('الاستخدام', {
            'fields': ('usage_limit', 'usage_limit_per_user', 'times_used')
        }),
        ('الصلاحية', {
            'fields': ('valid_from', 'valid_until', 'is_active')
        }),
    )


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'order', 'discount_amount', 'used_at']
    list_filter = ['used_at', 'coupon']
    search_fields = ['coupon__code', 'user__email']
    readonly_fields = ['coupon', 'user', 'order', 'discount_amount', 'used_at']
    ordering = ['-used_at']
    
    def has_add_permission(self, request):
        return False
