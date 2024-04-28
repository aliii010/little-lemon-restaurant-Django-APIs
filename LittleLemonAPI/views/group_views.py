from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from ..serializers import (
  UserSerializer, 
)
from ..custom_permissions import IsManager


class BaseGroupManagement(APIView):
  permission_classes = [IsManager]
  def get(self, request, group):
    group_members = User.objects.filter(groups__name=group)
    serializer = UserSerializer(group_members, many=True)
    return Response(serializer.data)
  
  def post(self, request, group):
    return self._helper_function(request, group=group, assign=True)
  
  def delete(self, request, group):
    return self._helper_function(request, group=group, assign=False)

  # a private helper function to add or remove user to the group
  def _helper_function(self, request, group, assign=True):
    username = request.data["username"]
    user = get_object_or_404(User, username=username)
    group = Group.objects.get(name=group)

    if assign:
      user.groups.add(group)
    else:
      user.groups.remove(group)

    return Response(
      {"msg": "success"},
      status=status.HTTP_201_CREATED if assign else status.HTTP_200_OK
    )

class Manager(BaseGroupManagement):
  def get(self, request):
    return super().get(request, group="Manager")

  def post(self, request):
    return super().post(request, group="Manager")
  
  def delete(self, request):
    return super().delete(request, group="Manager")


class DeliveryCrew(BaseGroupManagement):
  def get(self, request):
    return super().get(request, group="Delivery Crew")

  def post(self, request):
    return super().post(request, group="Delivery Crew")
  
  def delete(self, request):
    return super().delete(request, group="Delivery Crew")