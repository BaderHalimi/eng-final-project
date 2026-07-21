from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, Review


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    ordering = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discount_price', 'stock', 'is_active', 'is_featured', 'image_preview']
    list_filter = ['is_active', 'is_featured', 'category', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'discount_price', 'stock', 'is_active', 'is_featured']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'image_preview_large']
    inlines = [ProductImageInline]
    ordering = ['-created_at']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('الأسعار والمخزون', {
            'fields': ('price', 'discount_price', 'stock')
        }),
        ('الصورة', {
            'fields': ('image', 'image_preview_large')
        }),
        ('الحالة', {
            'fields': ('is_active', 'is_featured')
        }),
        ('معلومات إضافية', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "لا توجد صورة"
    image_preview.short_description = "الصورة"
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" style="border-radius: 10px;" />', obj.image.url)
        return "لا توجد صورة"
    image_preview_large.short_description = "معاينة الصورة"
    
    def save_model(self, request, obj, form, change):
        if not change:  # إذا كان منتج جديد
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating', 'created_at']
    search_fields = ['title', 'comment', 'user__username', 'product__name']
    list_editable = ['is_approved']
    readonly_fields = ['product', 'user', 'rating', 'title', 'comment', 'created_at']
    ordering = ['-created_at']
    
    actions = ['approve_reviews', 'reject_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"تم اعتماد {queryset.count()} تقييم")
    approve_reviews.short_description = "اعتماد التقييمات المحددة"
    
    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"تم رفض {queryset.count()} تقييم")
    reject_reviews.short_description = "رفض التقييمات المحددة"
