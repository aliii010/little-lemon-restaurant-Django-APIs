from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
  name = models.CharField(max_length=100)
  description = models.TextField(blank=True)

  def __str__(self):
    return self.name
  
  
class MenuItem(models.Model):
  PORTION_SIZES = (
    ('S', 'Small'),
    ('M', 'Medium'),
    ('L', 'Large'),
  )

  name = models.CharField(max_length=100)
  price = models.DecimalField(max_digits=6, decimal_places=2)
  category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='menu_items')
  description = models.TextField()
  portion_size = models.CharField(max_length=50, choices=PORTION_SIZES, blank=True)
  rating = models.FloatField(blank=True)
  image = models.ImageField(upload_to='menu-item-images/', blank=True, null=True)
  featured = models.BooleanField(default=False)

  def __str__(self):
    return self.name


class Reservations(models.Model):
  customer = models.ForeignKey(User, on_delete=models.PROTECT)
  num_of_guests = models.SmallIntegerField()
  reservation_date = models.DateField()


class Cart(models.Model):
  customer = models.ForeignKey(User, on_delete=models.PROTECT)
  menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
  quantity = models.SmallIntegerField()

  def get_price(self):
    return self.menuitem.price * self.quantity

  def __str__(self):
    return f"{self.customer.username}'s Cart item"
  class Meta:
    unique_together = ('menuitem', 'customer')


class Order(models.Model):
  customer = models.ForeignKey(User, on_delete=models.PROTECT)
  delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='delivery_crew', null=True, blank=True)
  status = models.BooleanField(default=False, db_index=True)
  date = models.DateField(db_index=True, null=True, blank=True)

  def get_total_price(self):
    return sum(item.get_price() for item in self.order_items.all()) # order_items is the related name

  def __str__(self):
    return f"{self.customer.username}'s order"


class OrderItem(models.Model):
  order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
  menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='menuitems')
  quantity = models.SmallIntegerField()

  def get_price(self):
    return self.menuitem.price * self.quantity
  
  class Meta:
    unique_together = ('order', 'menuitem')