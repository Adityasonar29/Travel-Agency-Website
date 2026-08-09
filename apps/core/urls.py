from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('destinations/', views.destinations_page, name='destinations'),
    path('destinations/<slug:slug>/', views.destination_detail, name='destination_detail'),
    path('tours/', views.tours_page, name='tours'),
    path('tours/<slug:slug>/', views.tour_detail, name='tour_detail'),
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),
    path('privacy-policy/', views.privacy_policy_page, name='privacy_policy'),
    path('terms-and-conditions/', views.terms_page, name='terms'),
]
