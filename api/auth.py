from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Attempt to read cookie
        token = request.COOKIES.get('access')
        if token is None:
            return None
        else:
            valid_token = self.get_validated_token(token)
            return self.get_user(valid_token), valid_token

