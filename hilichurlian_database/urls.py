from django.urls import path

from . import views

app_name = 'hilichurlian_database'
urlpatterns = [
	path('', views.index, name='index'),
	path('submit', views.data_entry, name='data_entry'),
	# for POST
	path('add_data', views.add_data, name='add_data'),
]