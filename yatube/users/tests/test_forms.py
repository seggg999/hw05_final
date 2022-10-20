
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserCreateFormTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_create_user(self):
        """Валидная форма создает нового пользователя."""
        user_count = User.objects.count()
        form_data = {
            'first_name': 'Ankl',
            'last_name': 'Bens',
            'username': 'ketchup',
            'email': 'ketchup@yandex.ru',
            'password1': 'AiVFCdkMW3YvHYC',
            'password2': 'AiVFCdkMW3YvHYC',
        }

        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name='Ankl',
                last_name='Bens',
                username='ketchup',
                email='ketchup@yandex.ru',
            ).exists()
        )
