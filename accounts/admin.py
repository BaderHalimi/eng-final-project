from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Address, UserActivity


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'is_active', 'email_verified', 'two_factor_enabled', 'last_login']
    list_filter = ['is_active', 'is_staff', 'email_verified', 'two_factor_enabled']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('معلومات إضافية', {
            'fields': ('phone', 'email_verified', 'two_factor_enabled', 'last_login_ip')
        }),
        ('الأمان', {
            'fields': ('failed_login_attempts', 'lockout_until', 'password_changed_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('معلومات إضافية', {
            'fields': ('email', 'phone')
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'city', 'country', 'address_type', 'is_default']
    list_filter = ['address_type', 'is_default', 'country']
    search_fields = ['full_name', 'city', 'user__email']
    ordering = ['-created_at']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'ip_address', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__email', 'ip_address']
    readonly_fields = ['user', 'activity_type', 'ip_address', 'user_agent', 'extra_data', 'created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
