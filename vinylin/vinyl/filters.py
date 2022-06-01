from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class StockFilter(admin.SimpleListFilter):
    title = _('Stock Status')
    parameter_name = 'storage'

    def lookups(self, request, model_admin):
        return ('in_stock', 'In Stock'), ('out_of_stock', 'Out of Stock')

    def queryset(self, request, queryset):
        if self.value() == 'in_stock':
            return queryset.filter(storage__quantity__gt=0)
        if self.value() == 'out_of_stock':
            return queryset.filter(storage__quantity__lt=1)
