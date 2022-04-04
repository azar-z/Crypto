from django.contrib import admin

from trade.models import Order
from user.models import User, Nobitex, Wallex, Exir, Account


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


class AccountInline(admin.TabularInline):
    model = Account


class OrdeInline(admin.TabularInline):
    model = Order


class UserAdmin(admin.ModelAdmin):
    inlines = [AccountInline, NobitexInline, WallexInline, ExirInline]

    fieldsets = (
        (None, {
            'fields': (('username', 'email'), ('phone_number', 'national_code', 'address'))
        }),
    )


class NobitexAdmin(admin.ModelAdmin):
    inlines = [OrdeInline]


admin.site.register(User, UserAdmin)
admin.site.register(Nobitex, NobitexAdmin)
admin.site.register(Wallex)
admin.site.register(Exir)
admin.site.register(Order)
