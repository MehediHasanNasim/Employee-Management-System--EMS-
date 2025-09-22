from django.urls import path, include
from .users import urlpatterns as user_urls

urlpatterns = [
    path('', include(user_urls)),
]