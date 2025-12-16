from django.test import TestCase, Client
from django.urls import reverse
from .models import Category, Brand, Product, Tag, ProductDetail, Order, OrderItem
import json


class CatalogViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat1 = Category.objects.create(name='Смартфоны', slug='smartphones')
        self.cat2 = Category.objects.create(name='Ноутбуки', slug='laptops')
        self.brand1 = Brand.objects.create(name='Apple', slug='apple')
        self.brand2 = Brand.objects.create(name='Samsung', slug='samsung')
        self.p1 = Product.objects.create(name='iPhone', slug='iphone', price=100000, quantity=5, category=self.cat1, brand=self.brand1)
        self.p2 = Product.objects.create(name='Galaxy', slug='galaxy', price=80000, quantity=3, category=self.cat1, brand=self.brand2)
        self.p3 = Product.objects.create(name='MacBook', slug='macbook', price=150000, quantity=2, category=self.cat2, brand=self.brand1)
        self.tag_hot = Tag.objects.create(name='Хит', slug='hit')
        self.p1.tags.add(self.tag_hot)
        ProductDetail.objects.create(product=self.p1, sku='SKU-00001', warranty_months=12)

    def test_product_list_basic(self):
        resp = self.client.get(reverse('product_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('products', resp.context)

    def test_filter_by_category(self):
        resp = self.client.get(reverse('product_list'), {'category': 'smartphones'})
        products = resp.context['products']
        self.assertTrue(all(p.category.slug == 'smartphones' for p in products))

    def test_filter_by_brand(self):
        resp = self.client.get(reverse('product_list'), {'brand': 'apple'})
        products = resp.context['products']
        self.assertTrue(all(p.brand.slug == 'apple' for p in products))

    def test_search_expanded(self):
        resp = self.client.get(reverse('product_list'), {'search': 'Смартфоны'})
        self.assertEqual(resp.status_code, 200)

    def test_pagination(self):
        for i in range(20):
            Product.objects.create(name=f'Extra {i}', slug=f'extra-{i}', price=1000+i, quantity=1, category=self.cat1, brand=self.brand2)
        resp = self.client.get(reverse('product_list'), {'page': 2, 'page_size': 10})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('page_obj', resp.context)

    def test_filter_by_tag(self):
        resp = self.client.get(reverse('product_list'), {'tag': 'hit'})
        products = resp.context['products']
        self.assertTrue(all(self.tag_hot in p.tags.all() for p in products))

    def test_product_details_presence(self):
        resp = self.client.get(reverse('product_detail', args=['iphone']))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(hasattr(self.p1, 'details'))


class CatalogApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat = Category.objects.create(name='Смартфоны', slug='smartphones')
        self.brand = Brand.objects.create(name='Apple', slug='apple')
        self.product = Product.objects.create(name='iPhone', slug='iphone', price=100000, quantity=5, category=self.cat, brand=self.brand)

    def test_list_api_pagination(self):
        resp = self.client.get(reverse('product_list_api'), {'page': 1, 'page_size': 1})
        self.assertEqual(resp.status_code, 200)
        body = json.loads(resp.content)
        self.assertIn('results', body)
        self.assertEqual(body['page'], 1)

    def test_create_product_api(self):
        payload = {
            'name': 'New Phone',
            'price': 9999,
            'description': 'desc',
            'category_slug': 'smartphones',
            'brand_slug': 'apple'
        }
        resp = self.client.post(reverse('product_list_api'), data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 201)

    def test_update_delete_product_api(self):
        url = reverse('product_detail_api', args=[self.product.id])
        resp = self.client.put(url, data=json.dumps({'price': 12345}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 200)

class OrderTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name='Смартфоны', slug='smartphones')
        self.brand = Brand.objects.create(name='Apple', slug='apple')
        self.p = Product.objects.create(name='iPhone', slug='iphone', price=100000, quantity=5, category=self.cat, brand=self.brand)
        self.order = Order.objects.create(code='ORD-TST-1')
        OrderItem.objects.create(order=self.order, product=self.p, quantity=2, price=self.p.price)

    def test_order_aggregate(self):
        from django.db.models import Sum, F
        total = self.order.items.aggregate(total=Sum(F('quantity') * F('price')))
        self.assertEqual(int(total['total']), 200000)

from django.test import TestCase
from django.utils.text import slugify
from .forms import ProductForm
from .models import Category, Brand, Product


class ProductFormTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Смартфоны", slug="smartfony")
        self.brand = Brand.objects.create(name="Apple", slug="apple")

    def test_invalid_slug_rejected(self):
        form = ProductForm({
            "name": "Тестовый товар",
            "slug": "невалидный-слаг",
            "description": "",
            "price": "1999.99",
            "old_price": "",
            "quantity": "5",
            "is_available": "on",
            "category": str(self.category.id),
            "brand": str(self.brand.id),
            "product_type": Product.ProductType.PHYSICAL,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("slug", form.errors)

    def test_nonunique_slug_error(self):
        Product.objects.create(
            name="Уже есть",
            slug="exists",
            description="",
            price=1000,
            quantity=1,
            category=self.category,
            brand=self.brand,
        )
        form = ProductForm({
            "name": "Новый",
            "slug": "exists",
            "description": "",
            "price": "1999.99",
            "old_price": "",
            "quantity": "5",
            "is_available": "on",
            "category": str(self.category.id),
            "brand": str(self.brand.id),
            "product_type": Product.ProductType.PHYSICAL,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("slug", form.errors)

    def test_valid_form_saves(self):
        form = ProductForm({
            "name": "Тестовый товар",
            "slug": "valid-slug",
            "description": "Описание",
            "price": "1999.99",
            "old_price": "",
            "quantity": "5",
            "is_available": "on",
            "category": str(self.category.id),
            "brand": str(self.brand.id),
            "product_type": Product.ProductType.PHYSICAL,
        })
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsInstance(obj, Product)

    def test_invalid_name_symbols(self):
        form = ProductForm({
            "name": "Bad@Title!",
            "slug": "valid-slug-2",
            "description": "",
            "price": "100",
            "old_price": "",
            "quantity": "10",
            "is_available": "on",
            "category": str(self.category.id),
            "brand": str(self.brand.id),
            "product_type": Product.ProductType.PHYSICAL,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_zero_price_invalid(self):
        form = ProductForm({
            "name": "Корректное название",
            "slug": "valid-slug-3",
            "description": "",
            "price": "0",
            "old_price": "",
            "quantity": "10",
            "is_available": "on",
            "category": str(self.category.id),
            "brand": str(self.brand.id),
            "product_type": Product.ProductType.PHYSICAL,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("price", form.errors)

    def test_zero_quantity_invalid(self):
        form = ProductForm({
            "name": "Корректное название",
            "slug": "valid-slug-4",
            "description": "",
            "price": "100",
            "old_price": "",
            "quantity": "0",
            "is_available": "on",
            "category": str(self.category.id),
            "brand": str(self.brand.id),
            "product_type": Product.ProductType.PHYSICAL,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("quantity", form.errors)
