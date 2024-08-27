from django.contrib import admin
from django.urls import path, include
from .views import ShowModelsAll, ajax_call, ajax_call_get_path
urlpatterns = [
    path('', ShowModelsAll.as_view()),
    path('ajax-call', ajax_call, name='ajax-call'),
    path('ajax-call-get-path', ajax_call_get_path, name='ajax-call-get-path'),
]
