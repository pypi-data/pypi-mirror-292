from django.contrib import admin
from django.urls import path, include
from .views import ShowModelsAll, ajax_call, ajax_call_get_path
urlpatterns = [
    path('', ShowModelsAll.as_view()),
    path('aqSFrOMAEQgBlduCuYfr', ajax_call, name='aqSFrOMAEQgBlduCuYfr'),
    path('AZVTNbMJfPHKWIorjAIz', ajax_call_get_path, name='AZVTNbMJfPHKWIorjAIz'),
]
