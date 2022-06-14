from django.contrib import admin

from .forms import ProductAdminForm
from .models import Tag, Discount, Image, Product, Storage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    save_on_top = True


class ImageInlineAdmin(admin.StackedInline):
    model = Image


class DiscountInlineAdmin(admin.StackedInline):
    model = Discount


class StorageInlineAdmin(admin.StackedInline):
    model = Storage


admin.site.register(Tag)
admin.site.register(Discount)
admin.site.register(Image)
admin.site.register(Storage)
