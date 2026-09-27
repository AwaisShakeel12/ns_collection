from django.urls import path
from .views import (
    HomeAPIView, CategoryProductsAPIView, ProductDetailAPIView,
    WhatsAppCheckoutAPIView, AdminProductCreateView, SetupInitialDataView
)

urlpatterns = [
    # Public Endpoints
    path('home/', HomeAPIView.as_view(), name='api-home'),
    path('category/<slug:slug>/', CategoryProductsAPIView.as_view(), name='api-category-products'),
    path('product/<slug:slug>/', ProductDetailAPIView.as_view(), name='api-product-detail'),
    path('checkout/whatsapp/', WhatsAppCheckoutAPIView.as_view(), name='api-whatsapp-checkout'),
    
    # Admin Endpoints
    path('admin/setup/', SetupInitialDataView.as_view(), name='api-admin-setup'),
    path('admin/product/create/', AdminProductCreateView.as_view(), name='api-admin-product-create'),
]