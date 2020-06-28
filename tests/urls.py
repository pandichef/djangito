# note: this is structured as if one project had both djangito_client and djangito__server running on it
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
                  path('admin/', admin.site.urls),  # name must be "admin"
                  path('o/', include('djangito_server.urls')),
                  path('oidc/', include('djangito_client.urls')),
              ]
