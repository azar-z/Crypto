import django_filters
from django_filters import FilterSet

from tagging.models import Tag


class TagFilterSet(FilterSet):
    text = django_filters.CharFilter(lookup_expr='icontains', label='Tag Text')

    class Meta:
        model = Tag
        fields = ['text', 'content_type', 'object_id']
