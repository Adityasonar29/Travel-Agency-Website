from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('destinations/', views.destinations_page, name='destinations'),
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),
]
