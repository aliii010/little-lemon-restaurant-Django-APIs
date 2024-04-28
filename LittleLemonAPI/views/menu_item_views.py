from rest_framework import generics
from rest_framework import permissions
from rest_framework.throttling import UserRateThrottle
from ..models import MenuItem
from ..serializers import (
  MenuItemSerializer,
)
from ..custom_permissions import IsManager


class MenuItemView(generics.ListCreateAPIView):
  queryset = MenuItem.objects.all()
  serializer_class = MenuItemSerializer
  throttle_classes = [UserRateThrottle]
  
  def get_permissions(self):
    permission_classes = []
    if self.request.method == "GET":
      permission_classes = [permissions.IsAuthenticated]
    else:
      permission_classes = [IsManager]
    
    return [permission() for permission in permission_classes]


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
  queryset = MenuItem.objects.all()
  serializer_class = MenuItemSerializer
  """
  default lookup_field is 'pk', I change it to the name of the item.
  also this must match the path segment in the url.
  """
  lookup_field = 'name'

  def get_permissions(self):
    permission_classes = []
    if self.request.method == "GET":
      permission_classes = [permissions.IsAuthenticated]
    else:
      permission_classes = [IsManager]
    
    return [permission() for permission in permission_classes]