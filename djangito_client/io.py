import logging
from django.contrib.auth import get_user_model
logger = logging.getLogger(__name__)


def save_user_string_fields(string_data: dict, user_model=get_user_model()):
    """Saves string fields into User model"""
    User = user_model
    try:
        user = User.objects.get(server_id=string_data['server_id'])
        for attr, value in string_data.items():
            setattr(user, attr, value)
    except User.DoesNotExist as e:
        logger.info(f"{repr(e)}")
        user = User(**string_data)
    user.save()
    return user


def save_user_foreign_key_fields(foreign_key_data, user_obj):
    """Saves foreign key fields into User model
    Note: This has only been tested on User.company as of 6/26/20
    """
    User = user_obj.__class__
    for field in foreign_key_data:
        try:
            ForeignKeyModel = User._meta.get_field(field).remote_field.model
            try:
                fkobj = ForeignKeyModel.objects.get(server_id=foreign_key_data[field]['server_id'])
                for attr, value in foreign_key_data[field].items():
                    setattr(fkobj, attr, value)
            except Exception as e:  # i.e., ForeignKey object does not exist
                logger.info(f"{repr(e)}")
                fkobj = ForeignKeyModel(**foreign_key_data[field])
            fkobj.save()
            setattr(user_obj, field, fkobj)
            user_obj.save()
            return True
        except Exception as e:
            logger.info(f'Could not find ForeignKey field {field}; ignoring data')
            return False
