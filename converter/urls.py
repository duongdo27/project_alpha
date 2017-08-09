from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^timestamp$', views.TimestampView.as_view(), name='timestamp'),
    url(r'^color$', views.ColorView.as_view(), name='color'),
    url(r'^base64$', views.Base64View.as_view(), name='base64'),
    url(r'^binary$', views.BinaryView.as_view(), name='binary'),
]
