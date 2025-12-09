from django.contrib import admin
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.db.models import F
from .models import Category, Brand, Product, Tag, ProductDetail, Order, OrderItem

class HasDiscountFilter(admin.SimpleListFilter):
    title = 'Со скидкой'
    parameter_name = 'has_discount'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'yes':
            return queryset.filter(old_price__gt=F('price'))
        if value == 'no':
            return queryset.exclude(old_price__gt=F('price'))
        return queryset

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
    list_display = ['name', 'price', 'old_price', 'discount_percent_edit', 'category', 'brand', 'is_available', 'status', 'created']
    list_filter = ['category', 'brand', 'is_available', 'status', 'created', 'tags', HasDiscountFilter]
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_available', 'status']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created', 'updated']
    filter_horizontal = ['tags']
    actions = ['mark_published', 'mark_unavailable', 'apply_discount_10']
    
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

    def discount_percent_edit(self, obj):
        try:
            if obj.old_price and obj.old_price > obj.price:
                percent = (float(obj.old_price) - float(obj.price)) * 100.0 / float(obj.old_price)
            else:
                percent = 0.0
            return mark_safe(
                f'<div class="discount-editor" data-product-id="{obj.id}">' \
                f'<input type="number" min="0" max="99" step="1" class="discount-input" value="{percent:.0f}" />%' \
                f'</div>'
            )
        except Exception:
            return mark_safe('<span>-</span>')
    discount_percent_edit.short_description = 'Скидка %'

    def mark_published(self, request, queryset):
        updated = queryset.update(status=Product.Status.PUBLISHED, is_available=True)
        messages.success(request, f"Опубликовано и доступно: {updated} товаров")
    mark_published.short_description = 'Опубликовать и сделать доступными'

    def mark_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        messages.warning(request, f"Недоступно: {updated} товаров")
    mark_unavailable.short_description = 'Сделать недоступными'

    def apply_discount_10(self, request, queryset):
        count = 0
        for p in queryset:
            try:
                old = float(p.price)
                p.old_price = p.old_price or old
                p.price = old * 0.9
                p.save(update_fields=['price','old_price'])
                count += 1
            except Exception:
                pass
        messages.info(request, f"Скидка 10% применена к {count} товарам")
    apply_discount_10.short_description = 'Применить скидку 10%%'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom = [
            path('update-discount/<int:product_id>/', self.admin_site.admin_view(self.update_discount), name='product_update_discount'),
        ]
        return custom + urls

    def update_discount(self, request, product_id):
        from django.http import JsonResponse
        from django.shortcuts import get_object_or_404
        product = get_object_or_404(Product, pk=product_id)
        if request.method != 'POST':
            return JsonResponse({'error': 'invalid_method'}, status=405)
        try:
            raw = request.POST.get('percent', '0')
            percent = max(0, min(99, int(float(raw))))
            old_price = float(product.old_price) if product.old_price else None
            if percent > 0:
                if old_price is None or old_price <= 0:
                    old_price = float(product.price)
                new_price = old_price * (100.0 - percent) / 100.0
                product.old_price = old_price
                product.price = max(0.0, new_price)
            else:
                if old_price is not None:
                    product.price = old_price
                product.old_price = None
            product.save(update_fields=['price','old_price'])
            data = {
                'success': True,
                'percent': percent,
                'price': f"{float(product.price):.2f}",
                'old_price': f"{float(product.old_price):.2f}" if product.old_price else None,
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    class Media:
        js = ('catalog/admin_product.js',)
        css = {'all': ('catalog/admin_product.css',)}

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
    can_delete = False
    max_num = 0
    readonly_fields = ('product', 'quantity_edit', 'price', 'item_sum', 'delete_action')
    fields = ('product', 'quantity_edit', 'price', 'item_sum', 'delete_action')

    def quantity_edit(self, obj):
        try:
            if obj.order.status in [Order.Status.NEW, Order.Status.PROCESSING]:
                return mark_safe(
                    f'<div class="inline-qty" data-item-id="{obj.id}">' \
                    f'<input type="number" min="1" class="inline-qty-input" value="{obj.quantity}" />' \
                    f'</div>'
                )
            return mark_safe(f'<span>{obj.quantity}</span>')
        except Exception:
            return mark_safe(f'<span>{obj.quantity}</span>')
    quantity_edit.short_description = 'Количество'

    def item_sum(self, obj):
        try:
            total = float(obj.price) * int(obj.quantity)
            return mark_safe(f'<span class="item-sum" data-item-id="{obj.id}">{total:.2f}</span>')
        except Exception:
            return mark_safe('<span class="item-sum">-</span>')
    item_sum.short_description = 'Сумма'

    def delete_action(self, obj):
        try:
            if obj.order.status in [Order.Status.NEW, Order.Status.PROCESSING]:
                return mark_safe(f'<button type="button" class="inline-delete-btn" data-item-id="{obj.id}">Удалить</button>')
            return ''
        except Exception:
            return ''
        
    delete_action.short_description = 'Действия'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['code', 'status', 'created', 'items_count', 'order_total']
    list_filter = ['status', 'created']
    inlines = [OrderItemInline]
    readonly_fields = ('created',)
    change_form_template = 'admin/catalog/order/change_form.html'
    fieldsets = (
        (None, {
            'fields': ('code', 'status', 'created')
        }),
    )

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom = [
            path('delete-item/<int:item_id>/', self.admin_site.admin_view(self.delete_item), name='orderitem_delete_inline'),
            path('add-item/<int:order_id>/', self.admin_site.admin_view(self.add_item), name='orderitem_add_inline'),
            path('update-item/<int:item_id>/', self.admin_site.admin_view(self.update_item), name='orderitem_update_inline'),
        ]
        return custom + urls

    def delete_item(self, request, item_id):
        from django.http import JsonResponse, HttpResponseForbidden
        from django.shortcuts import get_object_or_404
        item = get_object_or_404(OrderItem, pk=item_id)
        order = item.order
        if order.status not in [Order.Status.NEW, Order.Status.PROCESSING]:
            return HttpResponseForbidden('Удаление запрещено для завершённых заказов')
        if request.method != 'POST':
            return JsonResponse({'error': 'invalid_method'}, status=405)
        try:
            self.log_deletion(request, item, f'Удалена позиция {item.product} из заказа {order.code}')
            item.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def update_item(self, request, item_id):
        from django.http import JsonResponse, HttpResponseForbidden
        from django.shortcuts import get_object_or_404
        item = get_object_or_404(OrderItem, pk=item_id)
        order = item.order
        if order.status not in [Order.Status.NEW, Order.Status.PROCESSING]:
            return HttpResponseForbidden('Изменение запрещено для завершённых заказов')
        if request.method != 'POST':
            return JsonResponse({'error': 'invalid_method'}, status=405)
        try:
            qty = int(request.POST.get('quantity', '0'))
            if qty < 1:
                return JsonResponse({'error': 'invalid_quantity'}, status=400)
            old_qty = item.quantity
            item.quantity = qty
            item.save()
            self.log_change(request, item, f'Изменение количества {old_qty} → {qty} для товара {item.product} в заказе {order.code}')
            item_sum = float(item.price) * item.quantity
            order_total = sum(float(i.price) * i.quantity for i in order.items.all())
            return JsonResponse({'success': True, 'item_sum': f'{item_sum:.2f}', 'order_total': f'{order_total:.2f}'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def add_item(self, request, order_id):
        from django.shortcuts import get_object_or_404, redirect
        from django.http import HttpResponseForbidden
        from django.urls import reverse
        order = get_object_or_404(Order, pk=order_id)
        if order.status != Order.Status.NEW:
            return HttpResponseForbidden('Добавление доступно только для новых заказов')
        if request.method != 'POST':
            return redirect(reverse('admin:catalog_order_change', args=[order_id]) + '#add-item-modal')
        product_id = request.POST.get('product_id')
        qty = request.POST.get('quantity') or '1'
        try:
            product = Product.objects.get(pk=int(product_id))
            quantity = max(1, int(qty))
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=product.price)
            self.log_addition(request, order, f'Добавлен товар {product} (кол-во {quantity}) в заказ {order.code}')
        except Exception:
            pass
        return redirect(reverse('admin:catalog_order_change', args=[order_id]) + '#add-item-modal')

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        q = request.GET.get('q', '').strip()
        products = Product.objects.published()
        if q:
            products = products.filter(
                models.Q(name__icontains=q) |
                models.Q(details__sku__icontains=q)
            )
        products = products.select_related('brand', 'category')[:50]
        extra = extra_context or {}
        extra['add_product_query'] = q
        extra['add_product_results'] = products
        return super().changeform_view(request, object_id, form_url, extra)

    def total_amount(self, obj):
        total = sum(float(i.price) * i.quantity for i in obj.items.all())
        return mark_safe(f'<div id="order-total-amount">{total:.2f}</div>')
    total_amount.short_description = 'Итоговая сумма'

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Позиции'

    def order_total(self, obj):
        return f'{sum(float(i.price) * i.quantity for i in obj.items.all()):.2f}'
    order_total.short_description = 'Итог'

    class Media:
        js = ('catalog/admin_order.js',)
        css = {'all': ('catalog/admin_order.css',)}
