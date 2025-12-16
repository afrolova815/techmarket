from django.urls import path, register_converter
from . import views, converters

register_converter(converters.PriceRangeConverter, 'price_range')
register_converter(converters.StatusConverter, 'order_status')

urlpatterns = [
    path('', views.display_products, name='product_list'),
    path('add/', views.add_product, name='add_product'),
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('categories/', views.category_overview, name='category_list'),
    path('price/<price_range:price>/', views.price_filtered_products, name='price_filter'),
    path('brand/<slug:brand_identifier>/', views.brand_products, name='brand_filter'),
    path('orders/', views.order_management, name='order_list'),
    path('orders/<int:order_code>/', views.order_details, name='order_detail'),
    path('orders/status/<order_status:status>/', views.status_orders, name='status_orders'),
    path('legacy/<int:old_id>/', views.legacy_redirect, name='legacy_redirect'),
    path('category/<slug:category_slug>/', views.category_detail, name='category_detail'),
    path('orm-examples/', views.orm_examples, name='orm_examples'),
    path('api/products/', views.product_list_api, name='product_list_api'),
    path('api/products/<int:product_id>/', views.product_detail_api, name='product_detail_api'),
]
