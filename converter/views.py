from django.views.generic import TemplateView


class TimestampView(TemplateView):
    template_name = 'timestamp.html'


class ColorView(TemplateView):
    template_name = 'color.html'
