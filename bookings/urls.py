from django.urls import path
from . import views

urlpatterns = [
    # User views
    path('dashboard/', views.dashboard, name='dashboard'),
    path('travels/', views.travel_list, name='travel_list'),
    path('travels/<int:travel_id>/', views.travel_detail, name='travel_detail'),
    path('travels/<int:travel_id>/book/', views.booking_create, name='booking_create'),
    path('bookings/', views.booking_history, name='booking_history'),
    path('bookings/<int:booking_id>/cancel/', views.booking_cancel, name='booking_cancel'),
    
    # Admin views
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/travels/', views.admin_travels, name='admin_travels'),
    path('admin/travels/<int:travel_id>/edit/', views.admin_travel_edit, name='admin_travel_edit'),
    path('admin/travels/<int:travel_id>/delete/', views.admin_travel_delete, name='admin_travel_delete'),
    path('admin/bookings/', views.admin_bookings, name='admin_bookings'),
]
