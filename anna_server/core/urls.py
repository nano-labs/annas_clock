from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('image/<int:line>', views.image, name='image'),
    path('draw/', views.draw, name='image'),
]
