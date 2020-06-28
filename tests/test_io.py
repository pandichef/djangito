import pytest
from django.contrib.auth import get_user_model

from djangito_client.io import save_user_string_fields, save_user_foreign_key_fields


@pytest.fixture
def string_data():
    return {"date_joined": "2020-06-07T20:06:32Z",
            "is_superuser": True, "last_name": "Jackson",
            "last_login": "2020-06-26T20:20:44.522017Z",
            "username": "pandichef", "first_name": "Michael",
            "is_staff": True, "is_active": True,
            "email": "mike@gmail.com", "server_id": 1}


@pytest.fixture
def foreign_key_data():
    return {
        "company": {"name": "Jackson5", "primary_activity": 2, "server_id": 1}}


@pytest.mark.django_db
def test_save_user_string_fields(string_data) -> None:
    user = save_user_string_fields(string_data)
    assert user.__class__.objects.get(server_id=1) == user


@pytest.mark.django_db
def test_UPDATE_user_string_fields(string_data) -> None:
    get_user_model()(server_id=1, username='bradpitt').save()
    user = get_user_model().objects.get(server_id=1)
    original_pk = user.pk
    assert user.server_id == 1
    assert user.username == 'bradpitt'
    user = save_user_string_fields(string_data)
    assert user.server_id == 1
    assert user.username == 'pandichef'
    assert user.pk == original_pk


@pytest.mark.django_db
def test_UPDATE_user_foreign_key_fields(string_data, foreign_key_data) -> None:
    # Create ForeignKey field manually
    User = get_user_model()
    Company = User._meta.get_field('company').remote_field.model
    company = Company(server_id=1, name='Google')
    company.save()
    user = User(server_id=1, username='bradpitt')
    user.company = company
    user.save()
    # Update ForeignKey field
    user = save_user_string_fields(string_data)
    assert save_user_foreign_key_fields(foreign_key_data, user)
    assert user.server_id == 1
    assert user.username == 'pandichef'
    assert user.company.name == "Jackson5"
    new_foreign_key_data = {
        "company": {"name": "U2", "primary_activity": 2, "server_id": 2}}
    assert save_user_foreign_key_fields(new_foreign_key_data, user)
    assert user.company.name == "U2"


@pytest.mark.django_db
def test_save_user_foreign_key_fields_NOT_FOUND(string_data, foreign_key_data) -> None:
    user = save_user_string_fields(string_data)
    new_foreign_key_data = {
        "group": {"name": "U2", "primary_activity": 2, "server_id": 2}}
    assert not save_user_foreign_key_fields(new_foreign_key_data, user)
