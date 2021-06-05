from django.urls import path

from . import views

app_name = 'hilichurlian_database'
# be careful to not overlap with _project/urls.py
urlpatterns = [
	path('', views.index, name='index'),
	path('about', views.about, name='about'),
	path('submit', views.data_entry, name='data_entry'),
	# for POST
	path('add_data', views.add_data, name='add_data'),
]