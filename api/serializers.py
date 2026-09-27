from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    image = serializers.SerializerMethodField()
    display_price = serializers.SerializerMethodField()
    original_price = serializers.DecimalField(source='price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category', 'category_name',
            'image', 'original_price', 'display_price', 'discount_price',
            'external_link', 'is_sold', 'is_featured', 'created_at'
        ]

    def get_image(self, obj):
        request = self.context.get('request')
        img_url = obj.get_image
        
        # FIX: If it's a local uploaded file, build the absolute URL (http://127.0.0.1:8010/media/...)
        if img_url and request and img_url.startswith('/'):
            return request.build_absolute_uri(img_url)
        return img_url

    def get_display_price(self, obj):
        return obj.final_price

class ProductUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'price', 'discount_price',
            'image_file', 'image_url', 'external_link', 'is_sold', 'is_featured'
        ]

class CheckoutItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)

class WhatsAppCheckoutSerializer(serializers.Serializer):
    items = CheckoutItemSerializer(many=True)