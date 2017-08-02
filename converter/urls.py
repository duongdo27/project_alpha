from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^timestamp$', views.TimestampView.as_view(), name='timestamp'),
    url(r'^color$', views.ColorView.as_view(), name='color'),
]
