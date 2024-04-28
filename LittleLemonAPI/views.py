from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.throttling import UserRateThrottle
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from . models import MenuItem, Cart, Order, OrderItem,  Reservations
from . serializers import (
  MenuItemSerializer, 
  UserSerializer, 
  CartSerializer, 
  OrderSerializer,
  ReservationSerializer,
)
from . custom_permissions import IsManager


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
      

class ReservationView(APIView):
  def get(self, request):
    reservations = Reservations.objects.all()
    serializer = ReservationSerializer(reservations, many=True)
    return Response(serializer.data)
  
  def post(self, request):
    customer = request.user
    Reservations.objects.create(
      customer=customer,
      num_of_guests=request.data.get("num_of_guests"),
      reservation_date=request.data.get("reservation_date")
    )
    return Response({"msg": "Reservation Created Successfully"}, status=status.HTTP_201_CREATED)

#user group management views
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