from django.urls import path
from . import views

urlpatterns = [
  path("login/", views.CustomObtainAuthToken.as_view(), name='token-endpoint'), #login
  path('signup/', views.SignUpView.as_view(), name='singup-endpoint'),
  path('logout/', views.LogOutView.as_view(), name="logout-endpoint"),
  path('me/', views.UserView.as_view(), name='me'),
]
