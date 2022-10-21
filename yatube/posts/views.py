from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, Follow
from .utils import paginator_utils

User = get_user_model()

index_posts_pages: int = 10  # количество выводимых постов на гл. странице
group_posts_pages: int = 10  # количество выводимых постов в сообществе
authr_posts_pages: int = 10  # количество выводимых постов в профайле
follow_index_pages: int = 10  # количество выводимых постов в подписках


def index(request):
    '''Главная страница.'''
    post_list = Post.objects.select_related()
    page_obj = paginator_utils(request, post_list, index_posts_pages)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    '''Страницы сообщества.'''
    group = get_object_or_404(Group, slug=slug)
    group_list = group.posts.select_related()
    page_obj = paginator_utils(request, group_list, group_posts_pages)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    '''Страницы профайла.'''
    user_obj = get_object_or_404(User, username=username)
    authr_posts = user_obj.posts.select_related()
    count = authr_posts.count()
    page_obj = paginator_utils(request, authr_posts, authr_posts_pages)
    following = user_obj.following.select_related(
        'user').filter(user=request.user.id)
    context = {
        'user_obj': user_obj,
        'count': count,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    '''Страницы просмотра записи поста.'''
    post = get_object_or_404(Post, id=post_id)
    count = Post.objects.filter(author=post.author).count()
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'count': count,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    '''Страница создания записи поста.'''
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.method == "POST":
        if form.is_valid():
            form_buf = form.save(commit=False)
            form_buf.author_id = request.user.pk
            form_buf.save()
            return redirect('posts:profile', username=request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    '''Страница редактирования записи поста.'''
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.user.id != post.author.id:
        return redirect('posts:post_detail', post_id=post.id)
    elif request.method == 'POST':
        if form.is_valid():
            form.save()
        return redirect('posts:post_detail', post_id=post.id)
    context = {
        'is_edit': True,
        'form': form,
        'post': post,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    '''Сохранение комментария поста.'''
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    '''Страница просмотра постов авторов в подписке.'''
    follow = Follow.objects.filter(user=request.user)
    follow_list = Post.objects.filter(
        author__in=[fol.author for fol in follow])
    page_obj = paginator_utils(request, follow_list, follow_index_pages)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    '''Подписаться на автора.'''
    user_obj = get_object_or_404(User, username=username)
    if request.user.id == user_obj.id:
        return redirect('posts:profile', username=user_obj)
    follow = user_obj.following.select_related(
        'user',
        'author'
    ).filter(user=request.user)
    if not follow:
        user_obj.following.create(user=request.user)
    return redirect('posts:profile', username=user_obj)


@login_required
def profile_unfollow(request, username):
    '''Отписаться от автора.'''
    user_obj = get_object_or_404(User, username=username)
    unfollow = user_obj.following.filter(user=request.user)
    if unfollow:
        unfollow.delete()
    return redirect('posts:profile', username=user_obj)
