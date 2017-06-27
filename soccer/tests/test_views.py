from django.test import TestCase, RequestFactory

from ..views import HomeView


class BaseViewTest(TestCase):
    _view_class = None

    def setUp(self):
        self.factory = RequestFactory()

    def _get_response(self, request):
        response = self._view_class.as_view()(request)
        response.render()
        return response


class HomeViewTest(BaseViewTest):
    _view_class = HomeView

    def test(self):
        request = self.factory.get('/')
        response = self._get_response(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Welcome to Soccer Leagues!', response.content)
