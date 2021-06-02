from django.urls import path

from . import views

app_name = 'hilichurlian_database'
urlpatterns = [
	path('', views.index, name='index'),
]