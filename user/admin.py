from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.urls import reverse
from django.utils.html import format_html

from tagging.models import Tag
from trade.models import Order
from user.models import User, Nobitex, Wallex, Exir


class NobitexInline(admin.TabularInline):
    model = Nobitex


class WallexInline(admin.TabularInline):
    model = Wallex


class ExirInline(admin.TabularInline):
    model = Exir


class OrderInline(admin.TabularInline):
    model = Order
    fields = ['source_currency_type', 'time']
    show_change_link = True


class TagInline(GenericTabularInline):
    model = Tag


class UserAdmin(admin.ModelAdmin):
    inlines = [NobitexInline, WallexInline, ExirInline, OrderInline, TagInline]

    fieldsets = (
        (None, {
            'fields': (('first_name', 'last_name'), ('username', 'email'), ('phone_number', 'national_code', 'address'))
        }),
    )


class OrderAdmin(admin.ModelAdmin):
    inlines = [TagInline]

    list_display = ['name', 'next_step_link', 'previous_step_link']

    def name(self, obj):
        return str(obj)

    def link_to_related_step(self, related_step):
        if related_step is None:
            return '-'
        link = reverse("admin:trade_order_change", args=[related_step.id])
        return format_html('<a href="{}">{}</a>', link, related_step)

    def next_step_link(self, obj):
        return self.link_to_related_step(obj.next_step)
    next_step_link.allow_tags = True

    def previous_step_link(self, obj):
        return self.link_to_related_step(obj.previous_step)
    previous_step_link.allow_tags = True


class TagAdmin(admin.ModelAdmin):
    search_fields = ['content_type']


admin.site.register(User, UserAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Tag, TagAdmin)
