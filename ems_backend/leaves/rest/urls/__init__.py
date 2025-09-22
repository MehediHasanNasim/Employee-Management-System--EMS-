from django.urls import path, include
from .leaves import urlpatterns as leave_urls

urlpatterns = [
    path('', include(leave_urls)),
]