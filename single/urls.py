from django.urls import path
from . import views
from single.views import *
from django.conf import settings
from django.conf.urls.static import static


app_name = "single"

urlpatterns = [
    path("", views.indexpage, name="index_page"),
    path("upload", views.upload, name="upload"),
]