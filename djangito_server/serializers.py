from django.db.models.fields.related import ForeignKey
from rest_framework import serializers


def get_user_serializer(user_model):
    """Serializer for User model that includes all ForeignKey fields as nested
    JSON"""
    foreign_key_fields = [field for field in user_model._meta.fields if type(field) == ForeignKey]

    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = user_model
            exclude = ('server_id', 'password', 'groups', 'user_permissions')

    for field in foreign_key_fields:
        class UserSerializer(UserSerializer):
            class ForeignKeySerializer(serializers.ModelSerializer):
                class Meta:
                    model = field.remote_field.model
                    exclude = ('server_id',)

            exec(f"""{field.name} = ForeignKeySerializer(many=False, read_only=True)""")

    return UserSerializer
