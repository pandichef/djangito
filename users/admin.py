from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Company, User


class UserAdminPlus(UserAdmin):
    readonly_fields = ('is_staff', 'is_superuser', 'groups', 'user_permissions')
    list_display = ["username", "last_login", "company", "is_superuser", "is_staff", "is_active", "permission_groups"]
    search_fields = ('username', 'first_name', 'last_name', 'email',)  # Ref: https://stackoverflow.com/questions/5768165/django-search-fields-foreign-key-not-working
    fieldsets = (("User", {"fields": ("company",)}),) + (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    def permission_groups(self, obj) -> str:
        # tldr: this is to add field to changelist
        lst = []
        for group in obj.groups.all():
            lst.append(str(group))
        return ','.join(lst)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'primary_activity']


admin.site.register(User, UserAdminPlus)
admin.site.register(Company, CompanyAdmin)
