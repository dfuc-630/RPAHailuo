"""
URL configuration for imgvideo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,  include
from dev import views as dev2
from imgupload.views import upload_image_from_url
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('imgupload.urls')),
    path('api/upload-url/', upload_image_from_url, name='upload_image_from_url'),
    #path('api1/', dev2.callApi1),
    path('api2/', dev2.rpavideogen_loop),
]
