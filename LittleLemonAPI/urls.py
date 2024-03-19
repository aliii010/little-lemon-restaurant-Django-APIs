from django.urls import path
from . import views

urlpatterns = [
  path("menu-items/", views.MenuItemView.as_view(), name="menu-items"),
  path("menu-items/<slug:name>/", views.SingleMenuItemView.as_view(), name="single-menu-item"),
  path("cart/menu-items/", views.CartView.as_view(), name="cart"),
  path("orders/", views.OrderView.as_view(), name="order"),
  path("orders/<int:pk>/", views.SingleOrderView.as_view(), name="single-order"),
  path("groups/manager/users/", views.Manager.as_view(), name="managers"),
  path("groups/delivery-crew/users/", views.DeliveryCrew.as_view(), name="delivery-crew"),
]
