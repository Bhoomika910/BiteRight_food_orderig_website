from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class SoftTokenAuthentication(TokenAuthentication):
    """
    Like TokenAuthentication but if the token is invalid/expired,
    returns None (anonymous) instead of raising AuthenticationFailed.
    This lets AllowAny views work even when the client sends a stale token.
    Views that require IsAuthenticated still get protected — they just
    see an anonymous user instead of an error.
    """
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except AuthenticationFailed:
            # Bad token → treat as anonymous, don't raise
            return None
