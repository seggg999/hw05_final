
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, Comment
from django.conf import settings
import tempfile
import shutil

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_auth = User.objects.create_user(username='auth')
        cls.user_authorized = User.objects.create_user(username='no_auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание 1',
        )
        cls.group_edit = Group.objects.create(
            title='Тестовая группа edit',
            slug='test-slug-edit',
            description='Тестовое описание 2',
        )
        cls.group_no_edit = Group.objects.create(
            title='Тестовая группа no_edit',
            slug='test-slug-no',
            description='Тестовое описание 3',
        )
        cls.post_1 = Post.objects.create(
            author=cls.user_auth,
            text='Длинный тестовый пост',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        user_auth = PostCreateFormTests.user_auth
        user_authorized = PostCreateFormTests.user_authorized
        self.auth_client = Client()
        self.user_authorized_client = Client()
        self.guest_client = Client()
        self.auth_client.force_login(user_auth)
        self.user_authorized_client.force_login(user_authorized)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        group = PostCreateFormTests.group
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small_create.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Созданный тестовый пост',
            'group': group.id,
            'image': uploaded,
        }
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile',
                    kwargs={'username': self.user_auth.username})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                author=self.user_auth,
                image='posts/small_create.gif'
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редктирует запись в Post."""
        group_edit = PostCreateFormTests.group_edit
        post_1 = PostCreateFormTests.post_1
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small_edit.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Измененный тестовый пост',
            'group': group_edit.id,
            'image': uploaded,
        }
        response = self.auth_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': post_1.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post_1.id})
        )
        post_1.refresh_from_db()
        self.assertEqual(post_1.text, form_data['text'])
        self.assertEqual(post_1.group, group_edit)
        self.assertEqual(post_1.image, 'posts/small_edit.gif')

    def test_no_create_post(self):
        """Не авторизованный пользователь не может создать запись в Post."""
        post_count = Post.objects.count()
        group = PostCreateFormTests.group
        form_data = {
            'text': 'Создаем неавторизованный тестовый пост',
            'group': group.id,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertNotEqual(Post.objects.count(), post_count + 1)

    def test_guest_no_edit_post(self):
        """Не авторизованный пользователь не может редктировать запись в Post.
        """
        group_no_edit = PostCreateFormTests.group_no_edit
        post_1 = PostCreateFormTests.post_1
        form_data = {
            'text': 'Не авторизованный пользователь изменил пост',
            'group': group_no_edit.id,
        }
        response = self.guest_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': post_1.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{post_1.id}/edit/'
        )
        post_1.refresh_from_db()
        self.assertNotEqual(post_1.text, form_data['text'])
        self.assertNotEqual(post_1.group.slug, group_no_edit.slug)

    def test_no_auth_edit_post(self):
        """Не автор не может редктировать запись в Post."""
        group_no_edit = PostCreateFormTests.group_no_edit
        post_1 = PostCreateFormTests.post_1
        form_data = {
            'text': 'Не автор изменил пост',
            'group': group_no_edit.id,
        }
        response = self.user_authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': post_1.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, f'/posts/{post_1.id}/')
        post_1.refresh_from_db()
        self.assertNotEqual(post_1.text, form_data['text'])
        self.assertNotEqual(post_1.group.slug, group_no_edit.slug)

    def test_comment_creat_user_authorized(self):
        """Авторизованный пользователь может комментировать пост."""
        post_1 = PostCreateFormTests.post_1
        comm_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.user_authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': post_1.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': post_1.id}))
        self.assertEqual(Comment.objects.count(), comm_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
                post=post_1.id,
                author=self.user_authorized.id,
            ).exists()
        )

    def test_no_comment_creat_user_no_authorized(self):
        """Не вторизованный пользователь не может комментировать пост."""
        post_1 = PostCreateFormTests.post_1
        comm_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': post_1.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             f'/auth/login/?next=/posts/{post_1.id}/comment/')
        self.assertNotEqual(Comment.objects.count(), comm_count + 1)
