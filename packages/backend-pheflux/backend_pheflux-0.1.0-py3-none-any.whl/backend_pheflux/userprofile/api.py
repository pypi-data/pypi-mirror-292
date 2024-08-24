from ninja import NinjaAPI
from ninja.security import django_auth
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.shortcuts import get_object_or_404
from ninja import Schema
from .schemas import UserIn, UserOut, ChangePasswordIn
from .tokens import email_verification_token
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.http import Http404
from django.http import HttpResponse

User = get_user_model()

api = NinjaAPI()

@api.post("/register", response=UserOut)
def register_user(request, user_in: UserIn):
    user = User.objects.create_user(
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        phone_number=user_in.phone_number
    )
    user.is_active = False
    user.save()

    token = email_verification_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verification_link = request.build_absolute_uri(reverse('api-1.0.0:verify-email', args=[uid, token]))

    send_mail(
        'Verify your email',
        f'Click the link to verify your email: {verification_link}',
        'noreply@mydomain.com',
        [user.email],
    )

    return user

@api.get("/verify-email/{uid}/{token}",  tags=["auth"], url_name="verify-email")
def verify_email(request, uid: str, token: str):
    try:
        user = get_object_or_404(User, pk=urlsafe_base64_decode(uid).decode())
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        return {"message": "Email verified successfully."}
    else:
        raise Http404("Invalid or expired token.")

@api.post("/change-password")
def change_password(request, data: ChangePasswordIn):
    user = request.auth
    if not user.check_password(data.old_password):
        return {"error": "Wrong password"}, 400

    user.set_password(data.new_password)
    user.save()
    update_session_auth_hash(request, user)  # Keeps the user logged in after password change
    return {"status": "Password changed successfully."}

# Add more endpoints as needed
