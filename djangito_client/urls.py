from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import callback_handler, login_handler, push_server_data_to_client

urlpatterns = [
    path('login_handler/', login_handler, name='login_handler'),
    path('callback_handler/', csrf_exempt(callback_handler), name='callback_handler'),
    path('push_server_data_to_client/', push_server_data_to_client, name='push_server_data_to_client'),  # see djangito_server.signals
]
