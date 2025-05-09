# imgupload/urls.py

from django.urls import path
from . import views
from .views import upload_image_from_url
urlpatterns = [
     path('api/upload-url/', upload_image_from_url),
]
