from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from http import HTTPStatus

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_auth = User.objects.create_user(username='auth')
        cls.user_authorized = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_auth,
            text='Длинный тестовый пост',
            group=cls.group
        )

    def setUp(self):
        user_authorized = PostURLTests.user_authorized
        user_auth = PostURLTests.user_auth
        self.guest_client = Client()
        self.authorized_client = Client()
        self.auth_client = Client()
        self.authorized_client.force_login(user_authorized)
        self.auth_client.force_login(user_auth)

    def test_url_page_is_accessible_to_any_user(self):
        """Страница доступна любому пользователю."""
        user_authorized = PostURLTests.user_authorized
        post = PostURLTests.post
        url_names = [
            '/',
            f'/posts/{post.id}/',
            f'/group/{post.group.slug}/',
            f'/profile/{user_authorized.username}/',
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_page_is_available_to_authorized_user(self):
        """Страница доступна авторизованному пользователю."""
        user_authorized = PostURLTests.user_authorized
        post = PostURLTests.post
        url_names = [
            '/',
            '/create/',
            f'/posts/{post.id}/',
            f'/group/{post.group.slug}/',
            f'/profile/{user_authorized.username}/',
            '/follow/'
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_page_is_available_to_author(self):
        """Страница /posts/<int:post_id>/edit/ доступна автору."""
        post = PostURLTests.post
        response = self.auth_client.get(f'/posts/{post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_non_existent_page_404(self):
        """Несуществующая страница выдает ошибку 404."""
        url_names = [
            '/unexisting_page/'
            '/posts/666/',
            '/group/bad-slug/',
            '/profile/bad_user/',
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        user_authorized = PostURLTests.user_authorized
        post = PostURLTests.post
        templates_url_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{post.id}/': 'posts/post_detail.html',
            f'/posts/{post.id}/edit/': 'posts/create_post.html',
            f'/group/{post.group.slug}/': 'posts/group_list.html',
            f'/profile/{user_authorized.username}/': 'posts/profile.html',
            '/follow/': 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.auth_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_guest_client_redirect_page_is_correct(self):
        """Гость перенаправлен на правильную страницу."""
        post = PostURLTests.post
        url_names_redirect = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{post.id}/edit/':
            f'/auth/login/?next=/posts/{post.id}/edit/',
        }
        for address, redirect in url_names_redirect.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, redirect)

    def test_url_authorized_client_redirect_page_is_correct(self):
        """Не автор перенаправлен на правильную страницу."""
        post = PostURLTests.post
        response = self.authorized_client.get(f'/posts/{post.id}/edit/',
                                              follow=True)
        self.assertRedirects(response, f'/posts/{post.id}/')
