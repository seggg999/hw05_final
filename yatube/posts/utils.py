from django.core.paginator import Paginator


def paginator_utils(request, queryset, posts_pages):
    '''Утилита пажинатора
    posts_pages - количество выводимых постов пажинатором
    '''
    paginator = Paginator(queryset, posts_pages)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
