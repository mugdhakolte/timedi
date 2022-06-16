from rest_framework_simplejwt.authentication import JWTAuthentication as BaseJWTAuthentication
from .models import BlacklistedAccessToken


class JWTAuthentication(BaseJWTAuthentication):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header.
    """
    www_authenticate_realm = 'api'

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        validated_token = self.get_validated_token(raw_token)
        try:
            BlacklistedAccessToken.objects.get(token=str(validated_token), user_id=validated_token['user_id'])
            return None
        except BlacklistedAccessToken.DoesNotExist:
            return self.get_user(validated_token), None