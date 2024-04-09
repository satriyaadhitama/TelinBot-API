from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from .managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(_("Email"), max_length=254, unique=True)
    phone_number = PhoneNumberField(_("Nomor telepon"))
    position = models.CharField(max_length=100)
    image = models.ImageField(null=True, upload_to="images/users")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number", "position"]

    objects = UserManager()

    def __str__(self):
        return self.email
