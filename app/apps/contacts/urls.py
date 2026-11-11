from django.urls import path

from apps.contacts import views

app_name = 'contacts'

urlpatterns = [
    path('contacts/', views.contacts, name='contacts'),
    path('lead/', views.lead_create, name='lead'),
    path('thanks/', views.thanks, name='thanks'),
]
