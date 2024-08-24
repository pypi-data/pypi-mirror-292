from django.urls import path
from .views import UserRegistrationView, verify_email, ChangePasswordView
from .api import api

urlpatterns = [
    path("api/", api.urls),
]
