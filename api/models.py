from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager

# Create your models here.

# Custom user class to replace already existing model
class User(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('HC', 'Head Chef'),
        ('C', 'Chef'),
        ('DD', 'Delivery Driver'),
    )
    email = models.EmailField(verbose_name='email address', unique=True)
    name = models.CharField(max_length=255, blank=False)
    role = models.CharField(max_length=2, choices=ROLES)
    fridge_access = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


