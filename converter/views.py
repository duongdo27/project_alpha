from django.views.generic import TemplateView


class TimestampView(TemplateView):
    template_name = 'timestamp.html'
