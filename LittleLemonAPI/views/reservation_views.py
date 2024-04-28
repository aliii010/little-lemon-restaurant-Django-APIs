from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from ..models import Reservations
from ..serializers import (
  ReservationSerializer,
)

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