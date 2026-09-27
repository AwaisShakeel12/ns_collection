from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Product, StoreConfig

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'final_price', 'is_sold', 'is_featured')
    list_filter = ('category', 'is_sold', 'is_featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(StoreConfig)