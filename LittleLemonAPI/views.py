from rest_framework.response import Response
from rest_framework.decorators import api_view
from . models import MenuItem
from . serializers import MenuItemSerializer

@api_view()
def menu_items(request):
  menu_items = MenuItem.objects.all()
  serializer = MenuItemSerializer(menu_items, many=True)
  return Response(serializer.data)
