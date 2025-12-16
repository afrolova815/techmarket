from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_dashboard, name='main_dashboard'),
    path('add-record/', views.add_record, name='add_record'),
    path('upload/', views.upload_file, name='upload_file'),
    path('uploads/', views.uploaded_files_list, name='uploaded_files_list'),
]
