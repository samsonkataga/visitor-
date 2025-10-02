from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('checkin/', views.checkin, name='checkin'),
    path('checkout/', views.checkout, name='checkout'),
    path('badge/<str:badge_id>/', views.badge, name='badge'),
    path('reports/', views.reports, name='reports'),
    path('employees/', views.employees, name='employees'),
]