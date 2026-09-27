from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.shortcuts import get_object_or_404
import urllib.parse
from .models import Category, Product, StoreConfig
from .serializers import (
    CategorySerializer, ProductSerializer, 
    WhatsAppCheckoutSerializer, ProductUploadSerializer
)

class HomeAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        categories = Category.objects.all()
        home_data = {}
        for category in categories:
            featured_products = Product.objects.filter(
                category=category, is_featured=True
            ).order_by('-created_at')[:4]
            if featured_products.exists():
                home_data[category.slug] = {
                    "category_name": category.name,
                    "products": ProductSerializer(featured_products, many=True, context={'request': request}).data
                }
        return Response(home_data, status=status.HTTP_200_OK)

class CategoryProductsAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, slug):
        category = get_object_or_404(Category, slug=slug)
        products = Product.objects.filter(category=category).order_by('-created_at')
        return Response({
            "category": CategorySerializer(category).data,
            "products": ProductSerializer(products, many=True, context={'request': request}).data
        }, status=status.HTTP_200_OK)

class ProductDetailAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        return Response(ProductSerializer(product, context={'request': request}).data, status=status.HTTP_200_OK)

class WhatsAppCheckoutAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = WhatsAppCheckoutSerializer(data=request.data)
        if serializer.is_valid():
            items = serializer.validated_data['items']
            store_config = StoreConfig.load()
            wa_number = store_config.whatsapp_number
            
            # Clean, Professional WhatsApp Message (No messy image links)
            message = "Hello! I would like to place an order:\n\n"
            message += "*ORDER DETAILS*\n"
            message += "-------------------------\n"
            
            total_price = 0
            for item in items:
                product = get_object_or_404(Product, id=item['product_id'])
                qty = item.get('quantity', 1)
                price = product.final_price * qty
                total_price += price
                
                # WhatsApp uses *asterisks* for bold text
                message += f"*{product.name}*\n"
                message += f"Qty: {qty} | Price: {store_config.currency_symbol}{price}\n\n"
                
            message += "-------------------------\n"
            message += f"*TOTAL: {store_config.currency_symbol}{total_price}*\n\n"
            message += "Please confirm availability and share payment details. Thank you!"
            
            encoded_message = urllib.parse.quote(message)
            wa_link = f"https://wa.me/{wa_number}?text={encoded_message}"
            
            return Response({"whatsapp_link": wa_link, "message": message}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminUploadPermission:
    def check_admin_key(self, request):
        key = request.headers.get('X-Admin-Key') or request.query_params.get('admin_key')
        return key == settings.ADMIN_UPLOAD_KEY

class AdminProductCreateView(APIView, AdminUploadPermission):
    permission_classes = [AllowAny]
    def post(self, request):
        if not self.check_admin_key(request):
            return Response({"error": "Unauthorized admin key"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = ProductUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetupInitialDataView(APIView, AdminUploadPermission):
    permission_classes = [AllowAny]
    def post(self, request):
        if not self.check_admin_key(request):
            return Response({"error": "Unauthorized admin key"}, status=status.HTTP_401_UNAUTHORIZED)
        cats = ["Jewelry", "Clothing", "Other Top Items"]
        for c in cats:
            Category.objects.get_or_create(name=c)
        StoreConfig.load()
        return Response({"success": "Initial data seeded!"}, status=status.HTTP_201_CREATED)