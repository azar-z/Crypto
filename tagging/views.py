from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django_filters.views import FilterView

from tagging.filters import TagFilterSet
from tagging.models import Tag
from trade.utils import is_ajax


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class TagList(FilterView):
    model = Tag
    template_name = 'tagging/tag_list.html'
    context_object_name = 'tags'
    filterset_class = TagFilterSet
    paginate_by = 7


def get_tag_texts(request):
    if is_ajax(request):
        term = request.GET.get('term')
        tags = Tag.objects.filter(text__icontains=term)[:10]
        texts = list(tags.values_list('text', flat=True))
    else:
        texts = 'fail'
    return JsonResponse(texts, safe=False)
