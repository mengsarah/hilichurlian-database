from django.urls import path

from . import views

app_name = 'hilichurlian_database'
# be careful to not overlap with _project/urls.py
urlpatterns = [
	path('', views.index, name='index'),
	path('view', views.index, name='view'),
	path('about', views.about, name='about'),
	path('select', views.view_all_criteria, name='select'),
	path('filter', views.filter, name='filter'),
	# submissions are only ever temporarily open:
	# path('submit', views.data_entry, name='data_entry'),
	# for POST
	# path('add_data/<slug:submit_type>', views.add_data, name='add_data'),
]