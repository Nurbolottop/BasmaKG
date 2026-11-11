from django.urls import path

from apps.catalog import views

app_name = 'catalog'

urlpatterns = [
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/<slug:slug>/', views.catalog, name='category'),
    path('product/<slug:slug>/', views.product_detail, name='product'),
    path('order/', views.constructor, name='constructor'),
]
