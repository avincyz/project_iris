from urllib import request

from django.shortcuts import render

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def home(request):
    return Response({"message": f"Welcome {request.user.username}!"})

@api_view(['POST'])
# this handles the google login, google token should come from frontend
def google_login(request):
    token = request.data.get('id_token')
    # error if invalid or missing token
    if not token:
        return Response({"error": "No token provided"}, status = status.HTTP_400_BAD_REQUEST)

    try:
        # verifies the token, throws ValueError if token is invalid
        google_id = id_token.verify_oauth2_token(token, google_requests.Request())

        email = google_id.get('email')
        name = google_id.get('name')

        # get the user (or create new one if user does not exist yet)
        user_init = get_user_model()
        user, created = user_init.objects.get_or_create(email = email,
                                                   defaults = {
                                                       'username' : email,
                                                       'first_name' : name
                                                   })

        # create JWT tokens
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        response = Response({"message": "Successfully logged in!"}, status = status.HTTP_200_OK)

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
        return Response({"error": "Token is invalid"}, status = status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout(request):
    # deletes the cookies containing the tokens
    response = Response({"message": "Successfully logged out!"}, status = status.HTTP_200_OK)
    response.delete_cookie(key = 'access')
    response.delete_cookie(key = 'refresh')
    return response

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