from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, Cart, CartItem, Order, OrderItem, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_main']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discount_price', 'stock', 'is_active', 'is_featured', 'created_at']
    list_filter = ['category', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'discount_percentage_display']
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('Ціна та наявність', {
            'fields': ('price', 'discount_price', 'discount_percentage_display', 'stock')
        }),
        ('Налаштування', {
            'fields': ('image', 'is_active', 'is_featured')
        }),
        ('Дата створення', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def discount_percentage_display(self, obj):
        if obj.discount_percentage > 0:
            return f"{obj.discount_percentage}%"
        return "Немає знижки"
    discount_percentage_display.short_description = "Знижка"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'is_main']
    list_filter = ['is_main']
    search_fields = ['product__name', 'alt_text']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['added_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'total_items', 'total_price']
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'total_price', 'added_at']
    list_filter = ['added_at']
    search_fields = ['cart__user__username', 'product__name']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username', 'shipping_city']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('order_number', 'user', 'status', 'total_amount')
        }),
        ('Адреса доставки', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_zip_code', 'shipping_phone')
        }),
        ('Додаткова інформація', {
            'fields': ('notes',)
        }),
        ('Дата створення', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'total_price']
    list_filter = ['order__created_at']
    search_fields = ['order__order_number', 'product__name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['product__name', 'user__username', 'title']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('product', 'user', 'rating', 'title', 'comment')
        }),
        ('Модерація', {
            'fields': ('is_approved',)
        }),
        ('Дата створення', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# Налаштування адміністративної панелі
admin.site.site_header = "Terko Shop - Адміністративна панель"
admin.site.site_title = "Terko Shop Admin"
admin.site.index_title = "Управління магазином"