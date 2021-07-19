# importing django modules
from django.urls import path, include
from . import views as tracing_views
from django.conf.urls import url
from django.views.generic import TemplateView


# defining url routes and corresponding function to be called in views
urlpatterns = [
    url(r'^camerasNetworkGraph/', TemplateView.as_view(template_name="Tracing/graph.html"), name='camerasNetworkGraph'),
    url('getVehiclePath/', tracing_views.getVehiclePath, name = "getVehiclePath"),
    path('', tracing_views.homepage, name='homepage'),
]