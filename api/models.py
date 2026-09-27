from django.db import models
from django.utils.text import slugify

class StoreConfig(models.Model):
    """Singleton model to store global settings like your WhatsApp number."""
    store_name = models.CharField(max_length=100, default="My E-Commerce Store")
    # WhatsApp API requires country code. 0334 becomes 92334 for Pakistan.
    whatsapp_number = models.CharField(max_length=20, default="923346015655", help_text="Use country code without + or 00")
    currency_symbol = models.CharField(max_length=10, default="Rs.")

    def save(self, *args, **kwargs):
        self.pk = 1 # Force Singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.store_name

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    
    # PRICING
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, 
                                         help_text="Optional. Frontend will cross out original price if set.")
    
    # IMAGES (Upload OR Link)
    image_file = models.ImageField(upload_to='products/', blank=True, null=True, help_text="Upload from computer")
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Paste Pinterest/External image link")
    
    # STATUS & LINKS
    external_link = models.URLField(max_length=500, blank=True, null=True)
    is_sold = models.BooleanField(default=False, help_text="Check if item is sold")
    is_featured = models.BooleanField(default=False, help_text="Check to display on Home Page")
    
    created_at = models.DateTimeField(auto_now_add=True) # Used for "Latest Out" sorting
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def get_image(self):
        """Logic: If user uploaded a file, use it. Otherwise, fallback to URL."""
        if self.image_file:
            return self.image_file.url
        elif self.image_url:
            return self.image_url
        return None

    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price

    def __str__(self):
        return self.name