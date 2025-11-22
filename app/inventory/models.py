from django.db import models

# Create your models here.
class Category(models.Model):
    parent = models.ForeignKey('self', on_delete=models.RESTRICT, null=True, blank=True)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    is_active = models.BooleanField(default=False)
    level = models.SmallIntegerField(default=0)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    is_digital = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    price = models.IntegerField(default=0)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)


