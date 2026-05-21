from django.urls import path
from .views import *

urlpatterns = [
    path("drive/root", RootDriveView.as_view()),
    path("drive/folders/<int:pk>", FolderContentView.as_view()),

    path("folders/create/", FolderCreateView.as_view()),
    path("folders/<int:pk>", FolderUpdateDeleteView.as_view()),
    path("folders/<int:pk>/share", FolderShareView.as_view()),

    path("files/upload/", FileCreateView.as_view()),
    path("files/<int:pk>", FileUpdateDeleteView.as_view()),
    path("files/<int:pk>/download", FileDownloadView.as_view()),
    path("files/<int:pk>/share", FileShareView.as_view()),
]
