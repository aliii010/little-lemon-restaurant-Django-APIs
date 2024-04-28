from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from ..models import MenuItem, Cart
from ..serializers import (
  CartSerializer, 
)

class CartView(APIView):
  permission_classes = [permissions.IsAuthenticated]
  def get(self, request):
    cart_items = Cart.objects.filter(customer=request.user)
    serializer = CartSerializer(cart_items, many=True)
    return Response(serializer.data)

  def post(self, request):
    menu_item_id = request.data.get("menuitem_id")
    menu_item = get_object_or_404(MenuItem, pk=menu_item_id)
    quantity = request.data.get("quantity")
    Cart.objects.create(customer=request.user, menuitem=menu_item, quantity=quantity)
    return Response({"msg": "cart item created successfully"}, status=status.HTTP_201_CREATED)

  def delete(self, request):
    Cart.objects.filter(customer=request.user).delete()
    return Response({"msg": "all Cart items deleted"}, status=status.HTTP_200_OK)