from django.conf import settings
from django.core.paginator import Paginator


def paginator_page(request, queryset):
    return Paginator(queryset, settings.POST_PER_PAGE).get_page(request.GET.get("page"))
