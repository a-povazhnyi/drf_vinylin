from django.db import models
from django.urls import reverse

from .managers import VinylManager, VinylStockManager
from store.models import Product


class Country(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
        ordering = ['pk']


class Genre(models.Model):
    title = models.CharField(max_length=150)
    overview = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['pk']


class Artist(models.Model):
    name = models.CharField(max_length=200)
    overview = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'], name='name_idx')
        ]


class Vinyl(Product):
    vinyl_title = models.CharField(max_length=150)
    artist = models.ForeignKey(
        to=Artist,
        on_delete=models.CASCADE,
        null=True,
    )
    genres = models.ManyToManyField(Genre)
    country = models.ForeignKey(
        to=Country,
        null=True,
        on_delete=models.SET_NULL,
    )
    format = models.CharField(max_length=50, blank=True, null=True)
    credits = models.CharField(max_length=250, blank=True, null=True)

    objects = VinylManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('vinyl_single', kwargs={'pk': self.pk})

    class Meta:
        unique_together = ['vinyl_title', 'artist']


class VinylStock(Vinyl):
    class Meta:
        proxy = True

    objects = VinylStockManager()
