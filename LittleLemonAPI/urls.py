from django.urls import path
from .views import group_views, menu_item_views, cart_views, order_views, reservation_views


urlpatterns = [
  path("menu-items/", menu_item_views.MenuItemView.as_view(), name="menu-items"),
  path("menu-items/<slug:name>/", menu_item_views.SingleMenuItemView.as_view(), name="single-menu-item"),
  path("cart/menu-items/", cart_views.CartView.as_view(), name="cart"),
  path("orders/", order_views.OrderView.as_view(), name="order"),
  path("orders/<int:pk>/", order_views.SingleOrderView.as_view(), name="single-order"),
  path("reservations/", reservation_views.ReservationView.as_view(), name="reservation"),
  path("groups/manager/users/", group_views.Manager.as_view(), name="managers"),
  path("groups/delivery-crew/users/", group_views.DeliveryCrew.as_view(), name="delivery-crew"),
]
