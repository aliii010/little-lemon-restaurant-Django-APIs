from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ..models import Cart, Order, OrderItem
from ..serializers import (
  OrderSerializer,
)


class OrderView(APIView):
  permission_classes = [permissions.IsAuthenticated]
  # permission_classes = [permissions.IsAuthenticated, IsManager]
  def get(self, request):
    if not request.user.groups.exists():
      orders = Order.objects.filter(customer=request.user)
    elif request.user.groups.filter(name="Manager").exists():
      orders = Order.objects.all()
    elif request.user.groups.filter(name="Delivery Crew").exists():
      orders = Order.objects.filter(delivery_crew=request.user)

    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


  def post(self, request):
    order = Order.objects.create(customer=request.user)
    cart_items = Cart.objects.filter(customer=request.user)

    for item in cart_items:
      OrderItem.objects.create(order=order, menuitem=item.menuitem, quantity=item.quantity)
    
    cart_items.delete()
    return Response({"msg": "Order has been placed successfully"})


class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
  queryset = Order.objects.all()
  serializer_class = OrderSerializer
  permission_classes = [permissions.IsAuthenticated]

  def check_user_group(self, request, order):
    if not request.user.groups.exists(): # if user doesn't belong to any group
      if order.customer != request.user:
        raise PermissionDenied({"msg": "This order doesn't belong the current customer"})  
    elif request.user.groups.filter(name="Manger").exists():
      pass
    elif request.user.groups.filter(name="Delivery Crew").exists():
      if order.delivery_crew != request.user:
        raise PermissionDenied({"msg": "This order isn't assigned the current delivery crew"})

  def get_object(self):
    # same retrieving instance technique using pk, but with checking user group.
    order = super().get_object()
    self.check_user_group(self.request, order=order)
    return order
  

  def patch(self, request, *args, **kwargs):
    order = self.get_object()
    if request.user.groups.filter(name="Manager").exists():
        delivery_crew_id = request.data.get("delivery_crew_id")
        if delivery_crew_id:
          delivery_crew = get_object_or_404(User, id=delivery_crew_id)

          if not delivery_crew.groups.filter(name="Delivery Crew").exists():
              raise PermissionDenied({"msg": "Sorry, you cannot assign a non-delivery-crew user to an order."})

          serializer = OrderSerializer(order, data={'delivery_crew': delivery_crew_id}, partial=True)
          if serializer.is_valid():
              serializer.save()
              return Response(serializer.data, status=status.HTTP_200_OK)
          else:
              return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
          return Response({"msg": "delivery_crew_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.user.groups.filter(name="Delivery Crew").exists():
      entered_status = request.data.get("status")
      if entered_status in [0, 1]:
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
          serializer.save(update_fields=['status'])
        return Response(serializer.data, status=status.HTTP_200_OK)
      else:
        return Response({"msg": "status is required, 0 or 1."}, status=status.HTTP_400_BAD_REQUEST)
      