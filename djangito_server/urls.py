from django.shortcuts import HttpResponse
from django.urls import path, include
from .views import get_admin_url, profile  # this is the json user payload
# from .views import get_admin_url, UserDetails, UserList, GroupList

app_name = 'djangito_server'


def logout_and_boomerang(request) -> HttpResponse:
    # For djangito_server
    # todo move this to djangito
    from django.contrib.auth import logout
    from django.shortcuts import redirect
    logout(request)
    HTTP_REFERER = request.META.get('HTTP_REFERER')
    print(f'HTTP_REFERER: {HTTP_REFERER}')
    return redirect(HTTP_REFERER)


urlpatterns = [
    path('', include('oauth2_provider.urls')),
    path('get_admin_url/', get_admin_url, name='get_admin_url'),
    path('logout/', logout_and_boomerang, name='home'),
    path('profile/', profile, name='profile'),  # delivery the user data as JSON
]
