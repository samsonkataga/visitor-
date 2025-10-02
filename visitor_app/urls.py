from django.urls import path
from . import views
from .views import staff_reports_pdf


    


urlpatterns = [
    path('', views.home, name='home'),
    path('checkin/', views.checkin, name='checkin'),
    path('checkout/', views.checkout, name='checkout'),
    path('badge/<str:badge_id>/', views.badge, name='badge'),
    path('reports/', views.reports, name='reports'),
    path('employees/', views.employees, name='employees'),

    path('staff/registration/', views.staff_registration, name='staff_registration'),
    path('staff/checkin/', views.staff_checkin, name='staff_checkin'),
    path('staff/checkout/', views.staff_checkout, name='staff_checkout'),
    path('staff/list/', views.staff_list, name='staff_list'),
    path('staff/reports/', views.staff_reports, name='staff_reports'),

    path('staff/reports/pdf/', staff_reports_pdf, name='staff_reports_pdf'),
]