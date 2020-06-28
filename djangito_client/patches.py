# MONKEY PATCHES ADMIN URLS TO OIDC SERVER
# cf https://stackoverflow.com/questions/6779265/how-can-i-not-use-djangos-admin-login-view
import json

import requests
from django.conf import settings
from django.contrib.admin import sites
from django.urls import path
from django.urls.base import reverse_lazy
from django.views.generic.base import RedirectView


class DgangitoAdminSite(sites.AdminSite):
    def get_urls(self):
        default_urls = super().get_urls()
        res = requests.get(f"{settings.DJANGITO_SERVER_URL}/o/get_admin_url/")
        djangito_server_admin_url = json.loads(res.text).get('url', None)
        redirect_urls = [
            path('login/', RedirectView.as_view(
                url=reverse_lazy('login_handler'),
                permanent=False,
                query_string=True
            ), name='login'),
            path('password_change/', RedirectView.as_view(
                url=f'{settings.DJANGITO_SERVER_URL}{djangito_server_admin_url}',
                permanent=False,
                query_string=True
            ), name='password_change'),
        ]
        return redirect_urls + default_urls


# MONKEY PATCHING ADMIN SITE AND DJANGO SETTINGS
# https://stackoverflow.com/questions/6528723/changing-django-settings-at-runtime
sites.AdminSite = DgangitoAdminSite
settings.LOGOUT_REDIRECT_URL = f"{settings.DJANGITO_SERVER_URL}/o/logout/"  # fixme: This need to have callback to client site
settings.LOGIN_URL = reverse_lazy('login_handler')
