from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_Users_url_page_is_accessible_to_user(self):
        """Страница доступна зарегистрированному пользователю."""
        url_names = [
            '/auth/signup/',
            '/auth/login/',
            '/auth/password_reset_form/',
            '/auth/password_change/done/',
            '/auth/password_change/',
            '/auth/logout/',
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_Users_url_page_is_accessible_to_any_user(self):
        """Страница доступна любому пользователю."""
        url_names = [
            '/auth/signup/',
            '/auth/login/',
            '/auth/password_reset_form/',
            '/auth/logout/',
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_Users_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset_form/': 'users/password_reset_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
