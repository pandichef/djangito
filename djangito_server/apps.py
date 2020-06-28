from django.apps import AppConfig
from django.db.models.signals import post_save
from .signals import send_updated_user_data_to_client_applications


class DjangitoServerConfig(AppConfig):
    name = 'djangito_server'

    def ready(self):
        post_save.connect(send_updated_user_data_to_client_applications)
