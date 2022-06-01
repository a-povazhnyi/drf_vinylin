from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from .managers import OrderItemManager
from store.models import Product
from users.models import User


class Cart(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    is_reserved = models.BooleanField(default=False)

    def __str__(self):
        return f'({self.pk}) {self.user} Cart'

    def get_absolute_url(self):
        return reverse('cart', kwargs={'cart_pk': self.pk})


@receiver(post_save, sender=User)
def create_cart(sender, instance, created, **kwargs):
    """Creates cart object after user registration"""
    if created:
        Cart.objects.create(user=instance)


class Order(models.Model):
    STATUS_CHOICES = [
        ('NPA', 'not_paid'),
        ('PA', 'is_paid'),
        ('ODE', 'on_delivery'),
        ('DE', 'is_delivered'),
        ('CA', 'canceled'),
    ]

    user = models.ForeignKey(to=User, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=5, choices=STATUS_CHOICES)
    total_price = models.DecimalField(max_digits=7, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'({self.pk}) {self.user} Order'


class OrderItem(models.Model):
    cart = models.ForeignKey(
        to=Cart,
        null=True,
        on_delete=models.SET_NULL,
        related_name='order_items'
    )
    order = models.ForeignKey(
        to=Order,
        null=True,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    product = models.ForeignKey(
        to=Product,
        null=True,
        on_delete=models.SET_NULL,
    )
    quantity = models.SmallIntegerField(default=1)

    objects = OrderItemManager()
