from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Q, Avg, Count, Sum, F, Value, FloatField, Case, When, CharField
from django.core.paginator import Paginator, EmptyPage
from django.utils.text import slugify
from .models import Product, Category, Brand, Tag
from .forms import ProductForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView, DeleteView
from .mixins import DataMixin
import json

class ProductListView(DataMixin, ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        qs = Product.objects.published()
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        search_query = self.request.GET.get('search')
        if search_query:
            qs = qs.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(brand__name__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        active_category_slugs = self._active_set('category', 'categories')
        active_brand_slugs = self._active_set('brand', 'brands')
        active_tag_slugs = self._active_set('tag', 'tags', slugify_items=True)
        if active_category_slugs:
            qs = qs.filter(category__slug__in=list(active_category_slugs))
        if active_brand_slugs:
            qs = qs.filter(brand__slug__in=list(active_brand_slugs))
        if active_tag_slugs:
            qs = qs.filter(tags__slug__in=list(active_tag_slugs)).distinct()
        sort = self.request.GET.get('sort', '-created')
        if sort in ['price', '-price', 'name', '-name', '-created']:
            qs = qs.order_by(sort)
        qs = qs.annotate(
            discount_percent=Case(
                When(old_price__gt=F('price'), then=(F('old_price') - F('price')) * 100.0 / F('old_price')),
                default=Value(0.0),
                output_field=FloatField()
            ),
            source_label=Value('Каталог', output_field=CharField())
        )
        return qs

    def _active_set(self, singular, plural, slugify_items=False):
        active = set()
        single = self.request.GET.get(singular)
        if single:
            active.add(slugify(single) if slugify_items else single)
        param = self.request.GET.get(plural)
        if param:
            for s in param.split(','):
                if s:
                    active.add(slugify(s) if slugify_items else s)
        for s in self.request.GET.getlist(plural):
            for val in s.split(','):
                if val:
                    active.add(slugify(val) if slugify_items else val)
        for s in self.request.GET.getlist(singular):
            if s:
                active.add(slugify(s) if slugify_items else s)
        return active

    def get_paginate_by(self, queryset):
        page_size = self.request.GET.get('page_size', self.paginate_by)
        try:
            return int(page_size)
        except Exception:
            return self.paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_products = Product.objects.published()
        active_category_slugs = self._active_set('category', 'categories')
        active_brand_slugs = self._active_set('brand', 'brands')
        active_tag_slugs = self._active_set('tag', 'tags', slugify_items=True)
        categories_counts_qs = base_products
        if active_brand_slugs:
            categories_counts_qs = categories_counts_qs.filter(brand__slug__in=list(active_brand_slugs))
        if active_tag_slugs:
            categories_counts_qs = categories_counts_qs.filter(tags__slug__in=list(active_tag_slugs)).distinct()
        categories_counts = categories_counts_qs.values('category__slug', 'category__name').annotate(count=Count('id')).order_by('category__name')
        brands_counts_qs = base_products
        if active_category_slugs:
            brands_counts_qs = brands_counts_qs.filter(category__slug__in=list(active_category_slugs))
        if active_tag_slugs:
            brands_counts_qs = brands_counts_qs.filter(tags__slug__in=list(active_tag_slugs)).distinct()
        brands_counts = brands_counts_qs.values('brand__slug', 'brand__name').annotate(count=Count('id')).order_by('brand__name')
        tags_counts_qs = base_products
        if active_category_slugs:
            tags_counts_qs = tags_counts_qs.filter(category__slug__in=list(active_category_slugs))
        if active_brand_slugs:
            tags_counts_qs = tags_counts_qs.filter(brand__slug__in=list(active_brand_slugs))
        tags_counts = tags_counts_qs.values('tags__slug', 'tags__name').exclude(tags__slug__isnull=True).annotate(count=Count('id')).order_by('tags__name')
        facet_categories = [
            {
                'slug': c['category__slug'],
                'name': c['category__name'],
                'count': c['count'],
                'active': c['category__slug'] in active_category_slugs
            }
            for c in categories_counts
            if c['count'] > 0
        ]
        facet_brands = [
            {
                'slug': b['brand__slug'],
                'name': b['brand__name'],
                'count': b['count'],
                'active': b['brand__slug'] in active_brand_slugs
            }
            for b in brands_counts
            if b['count'] > 0
        ]
        facet_tags = [
            {
                'slug': t['tags__slug'],
                'name': t['tags__name'],
                'count': t['count'],
                'active': t['tags__slug'] in active_tag_slugs
            }
            for t in tags_counts
            if t['count'] > 0
        ]
        extras = self.get_user_context(**{
            'facet_categories': facet_categories,
            'facet_brands': facet_brands,
            'facet_tags': facet_tags,
            'active_category_slugs': list(active_category_slugs),
            'active_brand_slugs': list(active_brand_slugs),
            'active_tag_slugs': list(active_tag_slugs),
            'sort': self.request.GET.get('sort', '-created'),
            'title': 'Каталог товаров'
        })
        context.update(extras)
        return context

class OrderListView(View):
    def get(self, request):
        status_filter = request.GET.get('status', '')
        date_filter = request.GET.get('date', '')
        if status_filter or date_filter:
            filter_info = []
            if status_filter:
                filter_info.append(f"статус: {status_filter}")
            if date_filter:
                filter_info.append(f"дата: {date_filter}")
            return HttpResponse(f"Список заказов с фильтрами: {', '.join(filter_info)}")
        return HttpResponse("Все заказы системы")

class CategoryOverviewView(DataMixin, TemplateView):
    template_name = 'catalog/category_overview.html'


class CategoryDetailView(DataMixin, DetailView):
    model = Category
    template_name = 'catalog/category_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'category_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.published().filter(category=self.object)
        extras = self.get_user_context(**{
            'products': products,
            'title': f'Товары категории {self.object.name}'
        })
        context.update(extras)
        return context

class OrderDetailView(View):
    def get(self, request, order_code):
        return HttpResponse(f"Детали заказа: {order_code}")

class PriceFilteredProductsView(View):
    def get(self, request, price):
        return HttpResponse(f"Товары в ценовом диапазоне: {price['min']} - {price['max']}")

class BrandProductsView(View):
    def get(self, request, brand_identifier):
        return HttpResponse(f"Продукция бренда: {brand_identifier}")

class StatusOrdersView(View):
    def get(self, request, status):
        return HttpResponse(f"Заказы со статусом: {status}")


class ProductDetailView(DataMixin, DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'product_slug'

    def get_queryset(self):
        return Product.objects.published()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        similar_products = Product.objects.published().filter(
            category=product.category
        ).exclude(id=product.id)[:4]
        savings = None
        if getattr(product, 'has_discount', False) and product.old_price is not None:
            try:
                savings = float(product.old_price) - float(product.price)
            except Exception:
                savings = None
        extras = self.get_user_context(**{
            'similar_products': similar_products,
            'title': product.name,
            'savings': savings
        })
        context.update(extras)
        return context

class LegacyRedirectView(View):
    def get(self, request, old_id):
        return redirect('product_list', permanent=True)

class OrmExamplesView(View):
    def get(self, request):
        new_product = Product.objects.create(
            name='Новый товар',
            slug='new-product',
            price=50000,
            quantity=10,
            category=Category.objects.first(),
            brand=Brand.objects.first()
        )
        all_products = Product.objects.all()
        available_products = Product.objects.available()
        published_products = Product.objects.published()
        discounted_products = Product.objects.with_discount()
        apple_products = Product.objects.filter(brand__name='Apple')
        expensive_products = Product.objects.filter(price__gt=50000)
        smartphones = Product.objects.filter(category__name='Смартфоны')
        products_with_brand_category = Product.objects.select_related('brand', 'category')
        products_ordered_by_price = Product.objects.order_by('-price')
        price_stats = Product.objects.aggregate(
            avg_price=Avg('price'),
            total_products=Count('id'),
            total_value=Sum('price')
        )
        products_by_brand = Product.objects.values('brand__name').annotate(
            count=Count('id'),
            avg_price=Avg('price')
        )
        annotated = Product.objects.annotate(
            discount_percent=Case(
                When(old_price__gt=F('price'), then=(F('old_price') - F('price')) * 100.0 / F('old_price')),
                default=Value(0.0),
                output_field=FloatField()
            ),
            label=Value('ORM demo', output_field=CharField())
        ).values('name', 'discount_percent', 'label')[:5]
        Product.objects.filter(brand__name='Apple').update(price=F('price') * 0.9)
        context = {
            'total_products': all_products.count(),
            'available_count': available_products.count(),
            'apple_products_count': apple_products.count(),
            'price_stats': price_stats,
            'products_by_brand': list(products_by_brand),
            'annotated': list(annotated),
        }
        return JsonResponse(context)

@csrf_exempt
def product_list_api(request):
    """API для получения списка товаров и создания нового товара"""
    if request.method == 'POST':
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse({'error': 'invalid_json'}, status=400)

        name = payload.get('name')
        price = payload.get('price')
        description = payload.get('description', '')
        category_slug = payload.get('category_slug')
        brand_slug = payload.get('brand_slug')

        if not all([name, price, category_slug, brand_slug]):
            return JsonResponse({'error': 'missing_fields'}, status=400)

        try:
            category = Category.objects.get(slug=category_slug)
            brand = Brand.objects.get(slug=brand_slug)
        except Exception:
            return JsonResponse({'error': 'invalid_references'}, status=400)

        try:
            price_val = float(price)
        except Exception:
            return JsonResponse({'error': 'invalid_price'}, status=400)

        product = Product.objects.create(
            name=name,
            slug=slugify(name),
            description=description,
            price=price_val,
            category=category,
            brand=brand,
            is_available=True
        )
        data = {
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'price': float(product.price),
            'brand': product.brand.name,
            'category': product.category.name,
        }
        return JsonResponse(data, status=201)

    products = Product.objects.published().values(
        'id', 'name', 'slug', 'price', 'old_price', 
        'brand__name', 'category__name', 'is_available'
    )
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)
    try:
        page_size = int(page_size)
    except Exception:
        page_size = 10
    paginator = Paginator(list(products), page_size)
    try:
        page_obj = paginator.get_page(page)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)
    return JsonResponse({
        'results': list(page_obj.object_list),
        'page': page_obj.number,
        'pages': paginator.num_pages,
        'count': paginator.count
    })

@csrf_exempt
def product_detail_api(request, product_id):
    """API для работы с конкретным товаром"""
    if request.method == 'GET':
        product = get_object_or_404(Product, id=product_id)
        data = {
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'description': product.description,
            'brand': product.brand.name,
            'category': product.category.name,
        }
        return JsonResponse(data)
    if request.method == 'PUT':
        product = get_object_or_404(Product, id=product_id)
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse({'error': 'invalid_json'}, status=400)

        for field in ['name', 'description']:
            if field in payload:
                setattr(product, field, payload[field])
        if 'price' in payload:
            try:
                product.price = float(payload['price'])
            except Exception:
                return JsonResponse({'error': 'invalid_price'}, status=400)
        if 'category_slug' in payload:
            try:
                product.category = Category.objects.get(slug=payload['category_slug'])
            except Exception:
                return JsonResponse({'error': 'invalid_category'}, status=400)
        if 'brand_slug' in payload:
            try:
                product.brand = Brand.objects.get(slug=payload['brand_slug'])
            except Exception:
                return JsonResponse({'error': 'invalid_brand'}, status=400)
        product.save()
        return JsonResponse({'status': 'updated'})
    if request.method == 'DELETE':
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return JsonResponse({'status': 'deleted'})
    return JsonResponse({'error': 'method_not_allowed'}, status=405)
class ProductCreateView(DataMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/add_product.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Товар успешно добавлен')
        return redirect('product_list')

    def form_invalid(self, form):
        messages.error(self.request, 'Ошибка: проверьте корректность введённых данных')
        return render(self.request, self.template_name, self.get_user_context(form=form, title='Добавление товара'))

class ProductUpdateView(DataMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/add_product.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Товар обновлён')
        return redirect('product_detail', product_slug=self.object.slug)

    def form_invalid(self, form):
        messages.error(self.request, 'Ошибка обновления товара')
        return render(self.request, self.template_name, self.get_user_context(form=form, title=f'Редактирование: {getattr(self.object, "name", "")}'))

class ProductDeleteView(DataMixin, DeleteView):
    model = Product
    template_name = 'catalog/product_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, 'Товар удалён')
        return redirect('product_list').url
