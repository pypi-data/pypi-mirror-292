from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

class CustomUser(AbstractUser):
    # Add additional fields here if necessary
    phone_number = PhoneNumberField(
        unique=True, 
        null=True, 
        blank=True)

