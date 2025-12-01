from django.contrib import admin
from .models import Category, Brand, Product, Tag, ProductDetail, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'description']
    list_filter = ['name']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'description']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'old_price', 'category', 'brand', 'is_available', 'status', 'created']
    list_filter = ['category', 'brand', 'is_available', 'status', 'created', 'tags']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_available', 'status']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created', 'updated']
    filter_horizontal = ['tags']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description', 'category', 'brand')
        }),
        ('Цены и наличие', {
            'fields': ('price', 'old_price', 'quantity', 'is_available')
        }),
        ('Статус', {
            'fields': ('status',)
        }),
        ('Теги', {
            'fields': ('tags',)
        }),
        ('Даты', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        })
    )

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ProductDetail)
class ProductDetailAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'warranty_months']
    search_fields = ['product__name', 'sku']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['code', 'status', 'created']
    list_filter = ['status', 'created']
    inlines = [OrderItemInline]
