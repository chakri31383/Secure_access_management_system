# files/urls.py
from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    path('list/', views.files_list, name='list'),
    path('upload/', views.upload_file, name='upload'),
    path('<int:file_id>/download/', views.download_file, name='download'),
    path('<int:file_id>/edit/', views.edit_file, name='edit'),
    path('<int:file_id>/delete/', views.delete_file, name='delete'),
    path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('share/<int:file_id>/', views.share_file, name='share'),
]
