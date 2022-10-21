from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from http import HTTPStatus

User = get_user_model()


class AboutURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        address = '/unexisting_page/'
        template = 'core/404.html'
        response = self.guest_client.get(address)
        self.assertTemplateUsed(response, template)

    def test_error_page(self):
        """Открывается кастомная страница 404."""
        address = '/unexisting_page/'
        response = self.guest_client.get(address)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
