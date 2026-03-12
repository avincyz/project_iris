from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from gameplay.models import User

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def home(request):
    return Response({'message': f'Welcome {request.user.username}!'})

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    email = request.data.get('email')
    password = request.data.get('password')
    username = request.data.get('username', email)
    user_to_check = get_user_model()

    if not email or not password or not username:
        return Response({'error': 'All fields must be filled'}, status = status.HTTP_400_BAD_REQUEST)

    if user_to_check.objects.filter(email = email).exists():
        return Response({'error': 'The specified email has already been registered'}, status = status.HTTP_400_BAD_REQUEST)

    if user_to_check.objects.filter(username = username).exists():
        return Response({'error': 'The username is already taken'}, status = status.HTTP_400_BAD_REQUEST)

    user = user_to_check.objects.create_user(
        email = email,
        username = username,
        password = password
    )

    user.is_active = False
    user.save()

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    verify_link = f'http://localhost:8000/api/verify-email/{uid}/{token}/'

    send_mail(
        subject = 'Verify your email',
        message = f'Click the link to verify:\n{verify_link}',
        from_email='no-reply@localhost.com',
        recipient_list=[email],
    )

    return Response({'message': 'Successfully registered! Check email for verification link.'}, status = status.HTTP_201_CREATED)

@api_view(['POST'])
def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk = uid)
    except:
        return Response({'error': 'Invalid link'}, status = status.HTTP_400_BAD_REQUEST)

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        return Response({'message': 'Successfully verified! You may now log in.'}, status = status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid or expired token'}, status = status.HTTP_400_BAD_REQUEST)

# this is the login view
class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data['access']
            refresh_token = response.data['refresh']

            if access_token and refresh_token:

                # assign tokens to cookie
                response.set_cookie(key = 'access',
                                    value = access_token,
                                    httponly = True,
                                    samesite = 'Strict',
                                    secure = True,)
                response.set_cookie(key = 'refresh',
                                    value = refresh_token,
                                    httponly=True,
                                    samesite='Strict',
                                    secure=True,
                                    )
        return response

# this is the view for refreshing tokens
class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # get refresh token from cookie
        refresh_token = request.COOKIES.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token not found'}, status = status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data = {'refresh': refresh_token})
        serializer.is_valid(raise_exception = True)
        access = serializer.validated_data['access']

        response = Response({'message': 'Token refreshed!'})
        response.set_cookie(key = 'access', value = access, httponly = True,)
        return response

# this handles the Google login, google ID token should come from frontend
@api_view(['POST'])
def google_login(request):
    token = request.data.get('id_token')
    # error if invalid or missing token
    if not token:
        return Response({'error': 'No token provided'}, status = status.HTTP_400_BAD_REQUEST)

    try:
        # verifies the token, throws ValueError if token is invalid
        google_id = id_token.verify_oauth2_token(token, google_requests.Request())

        email = google_id.get('email')
        name = google_id.get('name')

        # get the user (or create new one if user does not exist yet)
        user_to_check = get_user_model()
        user, created = user_to_check.objects.get_or_create(
            email = email,
            defaults = {
               'username' : email,
               'first_name' : name
            })

        # create JWT tokens
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        response = Response({'message': 'Successfully logged in!'}, status = status.HTTP_200_OK)

        response.set_cookie(key = 'access',
                            value = str(access_token),
                            httponly = True,
                            samesite = 'Strict',
                            secure = True,)

        response.set_cookie(key = 'refresh',
                            value = str(refresh_token),
                            httponly = True,
                            samesite = 'Strict',
                            secure = True,)
        return response
    except ValueError:
        return Response({'error': 'Token is invalid'}, status = status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout(request):
    # deletes the cookies containing the tokens
    response = Response({'message': 'Successfully logged out!'}, status = status.HTTP_200_OK)
    response.delete_cookie(key = 'access')
    response.delete_cookie(key = 'refresh')
    return response

# this is the password change for a user that is already logged in
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def password_change(request):
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')

    if not old_password or not new_password:
        return Response({'error': 'All fields must be filled'}, status = status.HTTP_400_BAD_REQUEST)

    user = request.user
    # check if old password is correct
    if not user.check_password(old_password):
        return Response({'error': 'Incorrect old password'}, status = status.HTTP_400_BAD_REQUEST)
    # check if new password and confirm new password are the same
    if new_password != confirm_password:
        return Response({'error': 'New passwords do not match'}, status = status.HTTP_400_BAD_REQUEST)

    # if reached here, it means inputs are valid
    # set new password
    user.set_password(new_password)
    user.save()

    return Response({'message': 'Password changed successfully!'}, status = status.HTTP_200_OK)

# this is the password change for a user that is logged out (forgot password)
# this method handles sending the password reset email
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'No email provided'}, status = status.HTTP_400_BAD_REQUEST)

    user_to_check = get_user_model()
    try:
        user = user_to_check.objects.get(email = email)
    except user_to_check.DoesNotExist:
        return Response({'error': 'There is no existing user with the email provided'}, status = status.HTTP_400_BAD_REQUEST)

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    reset_link = f'http://localhost:8000/api/password-reset/{uid}/{token}/'

    send_mail(
        subject = 'Password reset',
        message = f'Reset Your Password: {reset_link}',
        from_email = 'no-reply@localhost.com',
        recipient_list = [email],
    )

    return Response({'message': 'Password reset email sent'}, status = status.HTTP_200_OK)

# this is the password change for a user that is logged out (forgot password)
# this method handles the actual password reset
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request, uidb64, token):
    new_password = request.data.get('new_password')
    if not new_password:
        return Response({'error': 'No new password provided'}, status = status.HTTP_400_BAD_REQUEST)

    user_to_check = get_user_model()
    # check for valid reset link
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = user_to_check.objects.get(pk = uid)
    except (user_to_check.DoesNotExist, ValueError):
        return Response({'error': 'Invalid link'}, status = status.HTTP_400_BAD_REQUEST)

    token_generator = PasswordResetTokenGenerator()
    if not token_generator.check_token(user, token):
        return Response({'error': 'Invalid or expired token'}, status = status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()
    return Response({'message': 'Password changed successfully!'}, status = status.HTTP_200_OK)