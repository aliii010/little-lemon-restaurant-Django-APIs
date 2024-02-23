from django.urls import path
from . import views

urlpatterns = [
  path('', views.menu_items),
  path("groups/manager/users/", views.Manager.as_view(), name="managers"),
  path("groups/delivery-crew/users/", views.DeliveryCrew.as_view(), name="delivery-crew"),
]
