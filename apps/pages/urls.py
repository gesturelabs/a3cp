from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('ui/', views.ui, name='ui'),
    path('docs/', views.docs, name='docs'),
]
