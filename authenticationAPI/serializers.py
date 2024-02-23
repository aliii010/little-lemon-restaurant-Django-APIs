from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = "__all__"

  # the process of creating a User model instance, it should go through the create_user method.
  # for example for password hashing.
  def create(self, validated_data):
    return User.objects.create_user(**validated_data)