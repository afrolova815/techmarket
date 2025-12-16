from django.urls import path, register_converter
from . import views, converters

register_converter(converters.PriceRangeConverter, 'price_range')
register_converter(converters.StatusConverter, 'order_status')

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('add/', views.ProductCreateView.as_view(), name='add_product'),
    path('product/<slug:product_slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('categories/', views.CategoryOverviewView.as_view(), name='category_list'),
    path('price/<price_range:price>/', views.PriceFilteredProductsView.as_view(), name='price_filter'),
    path('brand/<slug:brand_identifier>/', views.BrandProductsView.as_view(), name='brand_filter'),
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/<int:order_code>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/status/<order_status:status>/', views.StatusOrdersView.as_view(), name='status_orders'),
    path('legacy/<int:old_id>/', views.LegacyRedirectView.as_view(), name='legacy_redirect'),
    path('category/<slug:category_slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('orm-examples/', views.OrmExamplesView.as_view(), name='orm_examples'),
    path('api/products/', views.product_list_api, name='product_list_api'),
    path('api/products/<int:product_id>/', views.product_detail_api, name='product_detail_api'),
]
