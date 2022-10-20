from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Модель группы сообщества:
    title       - Имя,
    slug        - Адрес,
    description - Описание.
    """
    title = models.CharField(
        max_length=200,
        verbose_name='Имя группы',
    )
    slug = models.SlugField(
        verbose_name='Адрес',
        unique=True,
    )
    description = models.TextField(
        verbose_name='Описание группы',
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    """Модель запись сообщества:
    text       - Текст поста,
    pub_date   - Дата публикации,
    author     - Автор,
    group      - Сообщество.
    """
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts',
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    """Модель коментария сообщества:
    post — ссылка на пост, к которому оставлен комментарий,
    author — автор комментария,
    text — текст комментария,
    created — дата и время публикации,

    """
    post = models.ForeignKey(
        Post,
        verbose_name='Пост',
        help_text='Пост, к которой будет относиться комментарий',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-created']
        verbose_name = 'Коммент'
        verbose_name_plural = 'Комменты'


class Follow(models.Model):
    """Модель коментария сообщества:
    author — ссылка на объект пользователя, на которого подписываются,
    user  — ссылка на объект пользователя, который подписывается,
    """
    author = models.ForeignKey(
        User,
        verbose_name='Автор для подписки',
        on_delete=models.CASCADE,
        related_name='following',
    )
    user = models.ForeignKey(
        User,
        verbose_name='Подписанный пользователь',
        on_delete=models.CASCADE,
        related_name='follower',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
