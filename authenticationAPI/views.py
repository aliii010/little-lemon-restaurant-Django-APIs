from django.conf import settings
from django.conf import settings
from . serializers import UserSerializer
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

class CustomObtainAuthToken(ObtainAuthToken):
  def post(self, request, *args, **kwargs):
    response = super().post(request, *args, **kwargs)

    if response.status_code == 200:
      token = response.data.get('token')
      response.set_cookie(
        settings.AUTH_COOKIE,
        token,
        max_age=settings.AUTH_COOKIE_MAX_AGE,
        httponly=settings.AUTH_COOKIE_HTTP_ONLY
      )

    return response


class SignUpView(generics.CreateAPIView):
  serializer_class = UserSerializer


class LogOutView(APIView):
  def post(self, request):
    response = Response({"message": "logged out"} ,status=status.HTTP_200_OK)
    response.delete_cookie(settings.AUTH_COOKIE)

    return response


class UserView(generics.RetrieveAPIView):
  # query is not needed, cus get_object is overridden
  serializer_class = UserSerializer

  """
  By default, the lookup_field is the pk of the model instance, which retrieves a model instance based on a pk from the URL. 
  Since we already have the authenticated user stored in the request from the token stored in cookies, 
  there's no need for a queryset. Overriding the get_object method allows us to return the authenticated user directly.
  """
  def get_object(self):
    return self.request.user
