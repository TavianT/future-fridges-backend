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
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=255, blank=False)
    address = models.CharField(max_length=255, blank=False)
    contact_number = models.CharField(max_length=15, blank=False)
    email = models.EmailField(verbose_name='email address', unique=True)

    def __str__(self):
        return self.name

#Item model
class Item(models.Model):
    name = models.CharField(max_length=255)
    weight = models.FloatField()
    barcode = models.CharField(max_length=100)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class FridgeContent(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.FloatField()
    introduction_date = models.DateField(auto_now_add=True)
    expiration_date = models.DateField()
    last_inserted_by = models.ForeignKey(User, on_delete=models.CASCADE)

class Door(models.Model):
    name = models.CharField(max_length=10)
    door_locked = models.BooleanField()

    def __str__(self):
        return self.name




