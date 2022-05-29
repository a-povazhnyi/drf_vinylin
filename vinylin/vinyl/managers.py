from django.db import models


class VinylManager(models.Manager):
    def with_index_data(self):
        return (
            self.prefetch_related('images')
                .prefetch_related('tags')
                .select_related('discount')
        )

    def with_all_data(self):
        return (
            self.prefetch_related('images')
                .prefetch_related('tags')
                .prefetch_related('genres')
                .select_related('country')
                .select_related('discount')
                .select_related('artist')
        )


class VinylStockManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(storage__quantity__gt=0)
