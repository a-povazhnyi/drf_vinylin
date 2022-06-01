from django.contrib import admin
from django.db.models import F

from .filters import StockFilter
from .forms import VinylAdminForm
from .models import Country, Genre, Artist, Vinyl
from store.admin import (
    ImageInlineAdmin,
    StorageInlineAdmin,
    DiscountInlineAdmin
)
from store.models import Storage


@admin.register(Vinyl)
class VinylAdmin(admin.ModelAdmin):
    form = VinylAdminForm
    change_form_template = 'admin/vinyl_change_form.html'
    actions = ['decrease_quantity']

    list_display = ('id', 'title', 'price',
                    'price_with_discount', 'part_number')
    list_display_links = ('id', 'title')
    search_fields = ('vinyl_title',)
    list_filter = (StockFilter, 'genres')

    readonly_fields = ('created_at', 'price_with_discount')
    inlines = [ImageInlineAdmin, StorageInlineAdmin, DiscountInlineAdmin]

    save_on_top = True

    def get_fields(self, request, obj=None):
        """Moves price with discount to the right order"""
        fields = super().get_fields(request)
        price_with_discount = fields.pop()
        fields.insert(2, price_with_discount)
        return fields

    def change_view(self, request, object_id, form_url='', extra_context=None):
        vinyl = self.get_object(request, object_id)
        context = {'image_url': vinyl.images.first().image.url}
        return super().change_view(request, object_id,
                                   form_url, extra_context=context)

    def decrease_quantity(self, request, queryset):
        for vinyl in queryset:
            vinyl_storage = Storage.objects.get(product=vinyl)
            vinyl_storage.quantity = F('quantity') - 1
            vinyl_storage.save()
    decrease_quantity.short_description = "Decrease quantity by 1"

    @staticmethod
    def price_with_discount(obj):
        return str(obj.discount.price_with_discount)


admin.site.register(Country)
admin.site.register(Genre)
admin.site.register(Artist)
