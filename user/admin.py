from django.contrib import admin

from trade.models import Order
from user.models import User, Nobitex, Wallex, Exir


class NobitexInline(admin.TabularInline):
    model = Nobitex
    exclude = ['token']


class WallexInline(admin.TabularInline):
    model = Wallex
    exclude = ['token']


class ExirInline(admin.TabularInline):
    model = Exir
    exclude = ['api_key', 'api_signature']


class OrderInline(admin.TabularInline):
    model = Order


class UserAdmin(admin.ModelAdmin):
    inlines = [NobitexInline, WallexInline, ExirInline, OrderInline]

    fieldsets = (
        (None, {
            'fields': (('first_name', 'last_name'), ('username', 'email'), ('phone_number', 'national_code', 'address'))
        }),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Nobitex)
admin.site.register(Wallex)
admin.site.register(Exir)
admin.site.register(Order)
