from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models, transaction

from users.managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=500, unique=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name or ''} {self.last_name or ''}"

    def save(self, *args, **kwargs):
        from wallet.models import Wallet

        created = False
        if not self.pk:
            created = True

        with transaction.atomic():
            super().save(*args, **kwargs)

            if created:
                Wallet.objects.create(user=self)
