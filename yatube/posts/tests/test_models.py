from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Длинный тестовый пост',
        )

    def test_postmodels_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_postmodels_verbose_name(self):
        """verbose_name в полях  модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_postmodels_help_text(self):
        """help_text в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def test_groupmodels_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_groupmodels_verbose_name(self):
        """verbose_name в полях  модели Group совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Имя группы',
            'slug': 'Адрес',
            'description': 'Описание группы',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_comm = User.objects.create_user(username='commenter')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Длинный тестовый пост',
        )
        cls.comment = Comment.objects.create(
            author=cls.user_comm,
            text='Огромнийшей комментарий',
            post=cls.post
        )

    def test_commentmodels_have_correct_object_names(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        comment = CommentModelTest.comment
        expected_object_name = comment.text[:15]
        self.assertEqual(expected_object_name, str(comment))

    def test_commentmodels_verbose_name(self):
        """verbose_name в полях  модели Comment совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        field_verboses = {
            'post': 'Пост',
            'author': 'Автор',
            'text': 'Текст комментария',
            'created': 'Дата публикации',

        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name,
                    expected_value)

    def test_commentmodels_help_text(self):
        """help_text в полях модели Comment совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        field_help_texts = {
            'post': 'Пост, к которой будет относиться комментарий',
            'text': 'Введите текст комментария',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).help_text, expected_value)
