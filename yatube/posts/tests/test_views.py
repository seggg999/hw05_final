from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache.utils import make_template_fragment_key
from django.test import Client, TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse
from django import forms
from datetime import datetime
from unittest import mock
from pytz import utc
import tempfile
import shutil

from posts.models import Group, Post, Comment, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


def paginator_page_contains(self, adress: str, contex_page: str,
                            page_1: int, page_2: int
                            ) -> None:
    '''Утилита проверки паджинатора.
    adress      - адрес страницы с пажинатором;
    contex_page - передаваемый контекст в страницу;
    page_1      - число постов на первой странице;
    page_2      - число постов на второй странице.
    '''
    response = self.authorized_client.get(adress)
    self.assertEqual(len(response.context[contex_page]), page_1)
    if page_2 > 0:
        response = self.authorized_client.get(adress + '?page=2')
        self.assertEqual(len(response.context[contex_page]), page_2)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostWiewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_auth_1 = User.objects.create_user(username='auth')
        cls.user_auth_2 = User.objects.create_user(username='vova')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug-1',
            description='Тестовое описание 1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_1 = SimpleUploadedFile(
            name='small_1.gif',
            content=small_gif,
            content_type='image/gif'
        )
        uploaded_2 = SimpleUploadedFile(
            name='small_2.gif',
            content=small_gif,
            content_type='image/gif'
        )
        mocked = datetime(1018, 4, 4, 0, 0, 0, tzinfo=utc)
        with mock.patch('django.utils.timezone.now',
                        mock.Mock(return_value=mocked)):
            cls.post_0 = Post.objects.create(
                author=cls.user_auth_1,
                text='Длинный тестовый пост 0',
                group=cls.group_1,
                image=uploaded_1,
            )
        mocked = datetime(1019, 1, 2, 0, 0, 0, tzinfo=utc)
        with mock.patch('django.utils.timezone.now',
                        mock.Mock(return_value=mocked)):
            cls.post_1 = Post.objects.create(
                author=cls.user_auth_2,
                text='Длинный тестовый пост 2',
                group=cls.group_2,
                image=uploaded_2,
            )

        Follow.objects.create(
            user=cls.user_auth_2,
            author=cls.user_auth_1,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.auth_client = Client()
        self.authorized_client.force_login(self.user_auth_2)
        self.auth_client.force_login(self.user_auth_1)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post_0 = PostWiewsTests.post_0
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': post_0.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': post_0.author}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': post_0.id}):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': post_0.id}):
            'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for reverse_name, template, in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.auth_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_list_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        post = PostWiewsTests.post_0
        response = self.auth_client.get(reverse('posts:index'))
        third_object = response.context['page_obj'][1]
        templates_pages_contex = {
            post.author: third_object.author,
            post.pub_date: third_object.pub_date,
            post.id: third_object.id,
            post.group.slug: third_object.group.slug,
            post.group.id: third_object.group.id,
            post.text: third_object.text,
            post.image: third_object.image,
        }
        for post_contex, contex, in templates_pages_contex.items():
            with self.subTest(post_contex=post_contex):
                self.assertEqual(post_contex, contex)

    def test_group_list_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        post = PostWiewsTests.post_1
        response = self.auth_client.get(
            reverse('posts:group_list', kwargs={'slug': post .group.slug})
        )
        first_object = response.context['page_obj'][0]
        templates_pages_contex = {
            post.author: first_object.author,
            post.pub_date: first_object.pub_date,
            post.id: first_object.id,
            post.group.slug: first_object.group.slug,
            post.group.id: first_object.group.id,
            post.text: first_object.text,
            post.group: response.context['group'],
            post.image: first_object.image,
        }
        for post_contex, contex, in templates_pages_contex.items():
            with self.subTest(post_contex=post_contex):
                self.assertEqual(post_contex, contex)

    def test_profile_list_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        post = PostWiewsTests.post_1
        user_auth_2 = PostWiewsTests.user_auth_2
        response = self.auth_client.get(
            reverse('posts:profile', kwargs={'username': user_auth_2.username})
        )
        first_object = response.context['page_obj'][0]
        templates_pages_contex = {
            post.pub_date: first_object.pub_date,
            post.id: first_object.id,
            post.group.slug: first_object.group.slug,
            post.group.id: first_object.group.id,
            post.text: first_object.text,
            1: response.context['count'],
            post.author: response.context['user_obj'],
            post.image: first_object.image,
        }
        for post_contex, contex, in templates_pages_contex.items():
            with self.subTest(post_contex=post_contex):
                self.assertEqual(post_contex, contex)

    def test_post_detail_list_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        post = PostWiewsTests.post_0
        response = self.auth_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post.id}))
        first_object = response.context['post']
        templates_pages_contex = {
            post.pub_date: first_object.pub_date,
            post.id: first_object.id,
            post.group.slug: first_object.group.slug,
            post.group.title: first_object.group.title,
            post.text: first_object.text,
            post.author.id: first_object.author.id,
            1: response.context['count'],
            post.image: first_object.image,
        }
        for post_contex, contex, in templates_pages_contex.items():
            with self.subTest(post_contex=post_contex):
                self.assertEqual(post_contex, contex)

    def test_post_create_list_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.auth_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_list_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        post = PostWiewsTests.post_0
        response = self.auth_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post.id}))
        post_edit_is_edit = response.context['is_edit']
        post_object = response.context['post']
        post_edit_id = post_object.id
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertEqual(post_edit_is_edit, 1)
        self.assertEqual(post_edit_id, post.id)

    def test_follow_index_list_page_show_correct_context(self):
        """Шаблон follow_index сформирован с правильным контекстом."""
        post = PostWiewsTests.post_0
        response = self.authorized_client.get(reverse('posts:follow_index'))
        third_object = response.context['page_obj'][0]
        templates_pages_contex = {
            post.author: third_object.author,
            post.pub_date: third_object.pub_date,
            post.id: third_object.id,
            post.group.slug: third_object.group.slug,
            post.group.id: third_object.group.id,
            post.text: third_object.text,
            post.image: third_object.image,
        }
        for post_contex, contex, in templates_pages_contex.items():
            with self.subTest(post_contex=post_contex):
                self.assertEqual(post_contex, contex)

    def test_new_post_on_index_list_page(self):
        '''Новый пост появляется на главной странице сайта'''
        group_1 = PostWiewsTests.group_1
        new_post = Post.objects.create(
            author=self.user_auth_1,
            text='Новый длинный тестовый пост',
            group=group_1,
        )
        response = self.guest_client.get(reverse('posts:index'))
        object_page_obj = response.context['page_obj']
        ids = [post.id for post in object_page_obj]
        self.assertIn(new_post.id, ids)

    def test_new_post_on_group_list_page(self):
        '''Новый пост появляется на странице выбранной группы сайта'''
        group_1 = PostWiewsTests.group_1
        new_post = Post.objects.create(
            author=self.user_auth_1,
            text='Новый длинный тестовый пост',
            group=group_1,
        )
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': group_1.slug}))
        object_page_obj = response.context['page_obj']
        ids = [post.id for post in object_page_obj]
        self.assertIn(new_post.id, ids)

    def test_new_post_on_no_group_list_page(self):
        '''Новый пост не появляется на странице другой группы сайта'''
        group_1 = PostWiewsTests.group_1
        group_2 = PostWiewsTests.group_2
        new_post = Post.objects.create(
            author=self.user_auth_1,
            text='Новый длинный тестовый пост',
            group=group_1,
        )
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': group_2.slug}))
        object_page_obj = response.context['page_obj']
        ids = [post.id for post in object_page_obj]
        self.assertNotIn(new_post.id, ids)

    def test_new_post_on_profile_list_page(self):
        '''Новый пост появляется в профиле пользователя сайта'''
        user_auth_1 = PostWiewsTests.user_auth_1
        group_1 = PostWiewsTests.group_1
        new_post = Post.objects.create(
            author=self.user_auth_1,
            text='Новый длинный тестовый пост',
            group=group_1,
        )
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': user_auth_1.username})
        )
        object_page_obj = response.context['page_obj']
        ids = [post.id for post in object_page_obj]
        self.assertIn(new_post.id, ids)

    def test_new_comment_on_post_detail_page(self):
        '''Новый комментарий появляется на странице post_detail сайта'''
        post_0 = PostWiewsTests.post_0
        new_comment = Comment.objects.create(
            author=self.user_auth_2,
            text='Новый коммент к посту',
            post=post_0,
        )
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post_0.id})
        )
        object_page_comm = response.context['comments']
        ids = [comm.id for comm in object_page_comm]
        self.assertIn(new_comment.id, ids)

    def test_cache_index_page(self):
        '''Тэст кэша постов на странице index'''
        group_1 = PostWiewsTests.group_1
        new_post = Post.objects.create(
            author=self.user_auth_1,
            text='Пост для тэста кэша',
            group=group_1,
        )
        response = self.guest_client.get(reverse('posts:index'))
        new_post_content = response.content
        new_post.delete()
        response = self.guest_client.get(reverse('posts:index'))
        posts_cache_new_post = response.content
        self.assertEqual(new_post_content, posts_cache_new_post)
        key = make_template_fragment_key('index_page')
        cache.delete(key)
        response = self.guest_client.get(reverse('posts:index'))
        posts_cache_clear = response.content
        self.assertNotEqual(posts_cache_new_post, posts_cache_clear)

    def test_profile_follow_user_authorized(self):
        """Авторизованный пользователь может подписыватся на автора."""
        user_auth_2 = PostWiewsTests.user_auth_2
        user_auth_1 = PostWiewsTests.user_auth_1
        follow_count = Follow.objects.count()
        response = self.auth_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': user_auth_2.username}),
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': user_auth_2.username}))
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=user_auth_1,
                author=user_auth_2,
            ).exists()
        )

    def test_profile_unfollow_user_authorized(self):
        """Авторизованный пользователь может отписыватся от автора."""
        user_auth_2 = PostWiewsTests.user_auth_2
        user_auth_1 = PostWiewsTests.user_auth_1
        Follow.objects.create(
            user=user_auth_1,
            author=user_auth_2,
        )
        follow_count = Follow.objects.count()
        response = self.auth_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': user_auth_2.username}),
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': user_auth_2.username}))
        self.assertEqual(Follow.objects.count(), follow_count - 1)
        self.assertFalse(
            Follow.objects.filter(
                user=user_auth_1,
                author=user_auth_2,
            ).exists()
        )

    def test_new_post_appears_for_subscribers(self):
        """Новая запись автора появляется в ленте тех, кто на него подписан."""
        user_auth_2 = PostWiewsTests.user_auth_2
        user_auth_1 = PostWiewsTests.user_auth_1
        Follow.objects.create(
            user=user_auth_2,
            author=user_auth_1,
        )
        new_post = Post.objects.create(
            author=self.user_auth_1,
            text='Пост появляется у подписанта',
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        object_page_post = response.context['page_obj']
        ids = [post.id for post in object_page_post]
        self.assertIn(new_post.id, ids)

    def test_new_post_not_showing_up_for_subscribers(self):
        """Новая запись автора не появляется в ленте тех,
        кто на него не подписан."""
        user_auth_2 = PostWiewsTests.user_auth_2
        user_auth_1 = PostWiewsTests.user_auth_1
        Follow.objects.filter(
            user=user_auth_2,
            author=user_auth_1,
        ).delete()
        new_post = Post.objects.create(
            author=self.user_auth_1,
            text='Пост не появляется у не подписанта',
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        object_page_post = response.context['page_obj']
        ids = [post.id for post in object_page_post]
        self.assertNotIn(new_post.id, ids)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_follower = User.objects.create_user(username='followe')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts_db = []
        for i in range(13):
            cls.posts_db.append(Post(
                author=cls.user,
                text=f'Длинный тестовый пост {i}',
                group=cls.group
            ))
        Post.objects.bulk_create(cls.posts_db)
        Follow.objects.create(
            user=cls.user_follower,
            author=cls.user,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_follower)

    def test_index_page_contains_13_records(self):
        """Пажинатор страницы index работает правильно."""
        paginator_page_contains(self, adress=reverse('posts:index'),
                                contex_page='page_obj',
                                page_1=10,
                                page_2=3,
                                )

    def test_group_list_page_contains_13_records(self):
        """Пажинатор страницы group_list работает правильно."""
        group = PaginatorViewsTest.group
        paginator_page_contains(self,
                                adress=reverse(
                                    'posts:group_list',
                                    kwargs={'slug': group.slug}),
                                contex_page='page_obj',
                                page_1=10,
                                page_2=3,
                                )

    def test_profile_page_contains_13_records(self):
        """Пажинатор страницы profile работает правильно."""
        user = PaginatorViewsTest.user
        paginator_page_contains(self,
                                adress=reverse(
                                    'posts:profile',
                                    kwargs={'username': user.username}),
                                contex_page='page_obj',
                                page_1=10,
                                page_2=3,
                                )

    def test_follow_index_page_contains_13_records(self):
        """Пажинатор страницы follow работает правильно."""
        paginator_page_contains(self,
                                adress=reverse(
                                    'posts:follow_index'),
                                contex_page='page_obj',
                                page_1=10,
                                page_2=3,
                                )
