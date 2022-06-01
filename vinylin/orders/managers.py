from django.db.models import Manager, DecimalField, F, Q, Case, When


class OrderItemManager(Manager):
    def get_queryset(self):
        queryset = self.join_relevant(super().get_queryset())
        queryset = self.annotate_final_price(queryset)
        return queryset

    def annotate_final_price(self, queryset):
        price = F('product__price')
        quantity = F('quantity')
        discount_amount = F('product__discount__amount')
        discount_amount_not_null = Q(product__discount__amount__isnull=False)
        # Used to convert the discount percentage to a decimal fraction
        dec = self.get_decimal(0.01)

        return queryset.annotate(
            final_price=Case(
                When(
                    product__discount__amount=None,
                    then=price * quantity
                ),
                When(
                    product__discount__amount=discount_amount_not_null,
                    then=(price * (1 - (discount_amount * dec))) * quantity)
            )
        )

    @staticmethod
    def join_relevant(queryset):
        return (
            queryset.select_related('product', 'product__discount')
                    .prefetch_related('product__images')
                    .prefetch_related('product__tags')
        )

    @staticmethod
    def get_decimal(value):
        return DecimalField(
            max_digits=6, decimal_places=2
        ).clean(str(value), None)
