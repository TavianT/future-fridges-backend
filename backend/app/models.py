from django.db import models
from passlib.hash import pbkdf2_sha256
# Create your models here.
class User(models.Model):
    ROLES = (
        ('HC', 'Head Chef'),
        ('C', 'Chef'),
        ('DD', 'Delivery Driver'),
    )
    name = models.CharField(max_length=255, blank=False)
    email_address = models.EmailField(max_length=255)
    password = models.CharField(max_length=255, blank=False)
    role = models.CharField(max_length=2, choices=ROLES)
    fridge_access = models.BooleanField(default=True)

    def verify_password(self, raw_password):
        return pbkdf2_sha256.verify(raw_password, self.password)


