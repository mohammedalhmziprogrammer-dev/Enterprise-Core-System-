# accounts/services/auth_services.py

from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)

def force_logout_user(user):
    """
    Logout user from all devices immediately
    """
   
    user.token_version += 1
    user.save(update_fields=["token_version"])

    tokens = OutstandingToken.objects.filter(user=user)
    for token in tokens:
        BlacklistedToken.objects.get_or_create(token=token)
