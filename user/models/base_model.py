from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from tagging.models import Tag


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    tags = GenericRelation(Tag)

    class Meta:
        abstract = True

    def add_tag(self, tag_text):
        self.tags.create(text=tag_text)

    def to_dict(self):
        return self.__dict__
