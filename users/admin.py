from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import Group, GroupAdmin, UserAdmin
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from .models import Company, User


class ProtectedUserAdmin(UserAdmin):  # Ref: https://realpython.com/manage-users-in-django-admin/
    def get_readonly_fields(self, request, obj=None):
        # all_fields = [field.name for field in obj._meta.get_fields()]
        all_fields = [field.name for field in User._meta.get_fields()]  # need to commit later
        editable_fields = all_fields.copy()

        if request.user.is_superuser:
            pass
        elif request.user.is_staff:
            if obj.is_staff or obj.is_superuser:  # staff user cannot edit superusers and other staff users
                for field in all_fields:
                    editable_fields.remove(field)
            else:  # staff users cannot make regular users staff or superusers, but they can edit other fields
                editable_fields.remove('is_superuser')
                editable_fields.remove('is_staff')
        else:  # regular users cannot edit anything
            for field in all_fields:
                editable_fields.remove(field)

        if obj == request.user:  # notwithstanding the above, all users can edit their own first name, last name, email
            editable_fields.append('first_name')
            editable_fields.append('last_name')
            editable_fields.append('email')
        if 'last_login' in editable_fields:  # should never be editable
            editable_fields.remove('last_login')
        if 'date_joined' in editable_fields:  # should never be editable
            editable_fields.remove('date_joined')
        return list(set(all_fields)-set(editable_fields))


class ProtectedGroupAdmin(GroupAdmin):
    pass


class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'primary_activity']


class ProtectedAdminSite(AdminSite):
    site_header = 'Protected Admin Site'
    login_form = AuthenticationForm  # This is needed to override has_permission

    # Use this to allow non-staff users to authenticate
    # def has_permission(self, request):
    #     return request.user.is_active


protected_admin_site = ProtectedAdminSite(name='protected_admin_site')

protected_admin_site.register(User, ProtectedUserAdmin)
protected_admin_site.register(Group, ProtectedGroupAdmin)
protected_admin_site.register(Company, CompanyAdmin)  # Note: CompanyAdmin doesn't exist in base Django

# admin.site = protected_admin_site  # monkey patch default admin site

admin.site = protected_admin_site

# admin.site.register(User, ProtectedUserAdmin)
# admin.site.register(Company, CompanyAdmin)
