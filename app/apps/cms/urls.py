from django.urls import path

from apps.cms import views

app_name = 'cms'

urlpatterns = [
    path('services/', views.services, name='services'),
    path('services/<slug:slug>/', views.service_detail, name='service'),
    path('about/', views.about, name='about'),
    path('page/<slug:slug>/', views.page, name='page'),
]
