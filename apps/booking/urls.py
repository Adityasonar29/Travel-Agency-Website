from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.booking_page, name='booking'),
    path('book/<int:tour_pk>/', views.booking_page, name='booking_with_tour'),
    path('claim-draft/', views.claim_draft_booking, name='claim_draft'),
    path('confirmation/<str:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
]