from django.views.generic import TemplateView


class TimestampView(TemplateView):
    template_name = 'timestamp.html'


class ColorView(TemplateView):
    template_name = 'color.html'


class Base64View(TemplateView):
    template_name = 'base64.html'
