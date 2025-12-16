from django.urls import path
from . import views

urlpatterns = [
    path('', views.MainDashboardView.as_view(), name='main_dashboard'),
    path('add-record/', views.AddRecordView.as_view(), name='add_record'),
    path('upload/', views.UploadFileView.as_view(), name='upload_file'),
    path('uploads/', views.UploadedFilesListView.as_view(), name='uploaded_files_list'),
]
