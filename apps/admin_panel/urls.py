from django.urls import path
from . import views

app_name = "admin_panel"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("bookings/", views.bookings, name="bookings"),
    path("bookings/<int:pk>/", views.booking_detail, name="booking_detail"),
    path("bookings/<int:pk>/status/", views.update_booking_status, name="update_booking_status"),
    path("users/", views.users, name="users"),
    path("users/<int:pk>/delete/", views.delete_user, name="delete_user"),
    path("users/<int:pk>/toggle/", views.toggle_user, name="toggle_user"),
    path("tours/", views.tours, name="tours"),
    path("tours/add/", views.tour_form, name="tour_add"),
    path("tours/<int:pk>/edit/", views.tour_form, name="tour_edit"),
    path("tours/<int:pk>/delete/", views.delete_tour, name="tour_delete"),
    path("destinations/", views.destinations, name="destinations"),
    path("destinations/add/", views.destination_form, name="destination_add"),
    path("destinations/<int:pk>/edit/", views.destination_form, name="destination_edit"),
    path("destinations/<int:pk>/delete/", views.delete_destination, name="destination_delete"),
    path("payments/", views.payments, name="payments"),
    path("invoices/", views.invoices, name="invoices"),
]
