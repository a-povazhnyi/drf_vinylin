from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField

from users.managers import UserManager
from users.validators import birthday_validator
from vinyl.models import Country


class User(AbstractUser):
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    username = None
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)

    objects = UserManager()

    def __str__(self):
        return f'({self.pk}) {self.email}'

    def get_absolute_url(self):
        return reverse('profile', kwargs={'pk': self.pk})


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = PhoneNumberField(blank=True, null=True)
    birthday = models.DateField(
        blank=True,
        null=True,
        validators=[birthday_validator]
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='countries'
    )
    balance = models.DecimalField(default=0, max_digits=6, decimal_places=2)

    def __str__(self):
        return f'{self.user} ({self.pk})'

    def clean(self):
        if float(self.balance) < 0.00:
            raise ValidationError(
                _('You have not enough balance')
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def age(self):
        if not self.birthday:
            return None

        current_date = datetime.today().date()
        return int((current_date - self.birthday).days / 365.2425)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
