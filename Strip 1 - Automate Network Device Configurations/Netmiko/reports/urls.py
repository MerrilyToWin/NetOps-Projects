from django.urls import path
from . import views

urlpatterns = [
    path("reports/",views.get_results, name="get_results"),
]
