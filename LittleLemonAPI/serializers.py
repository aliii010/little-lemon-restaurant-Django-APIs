from rest_framework import serializers
from .models import MenuItem, Cart, OrderItem, Order, Category, Reservations
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = Category
    fields = "__all__"

class MenuItemSerializer(serializers.ModelSerializer):
  category = CategorySerializer()
  class Meta:
    model = MenuItem
    fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
  customer = UserSerializer()
  menuitem = MenuItemSerializer()
  price = serializers.SerializerMethodField(method_name='get_price')
  class Meta:
    model = Cart
    fields = "__all__"

  def get_price(self, obj:Cart):
    return obj.get_price()


class OrderItemSerializer(serializers.ModelSerializer):
  price = serializers.SerializerMethodField(method_name='get_price')
  menuitem = MenuItemSerializer()
  class Meta:
    model = OrderItem
    exclude = ("order",)

  def get_price(self, obj:OrderItem):
    return obj.get_price()

class OrderSerializer(serializers.ModelSerializer):
  customer = UserSerializer()
  delivery_crew = UserSerializer()
  order_items = OrderItemSerializer(many=True, read_only=True)
  class Meta:
    model = Order
    fields = "__all__"


class ReservationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Reservations
    exclude = ["customer"]

