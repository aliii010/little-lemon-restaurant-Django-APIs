from django.contrib import admin
from . models import Reservations, MenuItem, Category, Order, OrderItem

# Register your models here.

admin.site.register(Reservations)
admin.site.register(MenuItem)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)