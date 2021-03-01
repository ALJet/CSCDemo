from django import template
from django.urls import reverse
from six.moves.urllib.parse import urlencode,urlparse,parse_qs

register = template.Library()

@register.simple_tag
def change_url(request, kwargs=None, query=None):
    kwargs = kwargs or {}
    query = query or {}
    rm = request.resolver_match
    _kwargs = rm.kwargs.copy()
    _kwargs.update(kwargs)
    if _kwargs.get("page") == 1:
        _kwargs.pop("page", None)
    qs = parse_qs(urlparse(request.get_full_path()).query)
    qs.update(query)
    #这个需要改一下 有没有命名空间
    path = reverse('%s' % ( rm.url_name), args=rm.args, kwargs=_kwargs, )
    if (qs):
        return "%s?%s" % (path, urlencode(qs, True))
    else:
        return path


@register.simple_tag
def change_page(request, page=1):
    return change_url(request, {"page": page})


@register.simple_tag
def change_lpg_ordering(request, ordering):
    return change_url(request, None, {"order": ordering})


# 这个分页函数 看不懂啊 一系列的判断 好像就是让显示项数 在5
@register.inclusion_tag('pagination.html', takes_context=True)
def get_pagination(context, first_last_amount=2, before_after_amount=4):
    page_obj = context['page_obj']
    # print('page_obj' ,page_obj)


    paginator = context['paginator']
    is_paginated = context['is_paginated']
    # print('page_obj', page_obj)
    # print('paginator', paginator)
    # print('is_paginated', is_paginated)
    page_numbers = []

    if page_obj.number > first_last_amount + before_after_amount:
        for i in range(1, first_last_amount + 1):
            page_numbers.append(i)

        if first_last_amount + before_after_amount + 1 != paginator.num_pages:
            page_numbers.append(None)

        for i in range(page_obj.number - before_after_amount, page_obj.number):
            page_numbers.append(i)

    else:
        for i in range(1, page_obj.number):
            page_numbers.append(i)

    if page_obj.number + first_last_amount + before_after_amount < paginator.num_pages:
        for i in range(page_obj.number, page_obj.number + before_after_amount + 1):
            page_numbers.append(i)

        page_numbers.append(None)

        for i in range(paginator.num_pages - first_last_amount + 1, paginator.num_pages + 1):
            page_numbers.append(i)

    else:
        for i in range(page_obj.number, paginator.num_pages + 1):
            page_numbers.append(i)

    return {
        'paginator': paginator,
        'page_obj': page_obj,
        'page_numbers': page_numbers,
        'is_paginated': is_paginated,
        'request': context['request'],
    }
