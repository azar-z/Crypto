from django.contrib import admin

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


class UserAdmin(admin.ModelAdmin):
    inlines = [NobitexInline, WallexInline, ExirInline]

    fieldsets = (
        (None, {
            'fields': (('username', 'password'), ('phone_number', 'national_code'), 'address', 'avatar')
        }),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Nobitex)
admin.site.register(Wallex)
admin.site.register(Exir)
