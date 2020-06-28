import json
from datetime import timedelta

import pytest
import requests
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.utils import timezone

from oauth2_provider.models import AccessToken


@pytest.fixture
def mock_response(monkeypatch):
    class MockResponse:
        text = """{"url": "mock_response"}"""
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: MockResponse())


def test_get_admin_url(client, settings, monkeypatch, mock_response) -> None:
    response = client.get(reverse('djangito_server:get_admin_url'))
    json_payload = response.content.decode('utf-8')
    assert response.status_code == 200
    assert json.loads(json_payload)['url'] == reverse('admin:password_change')


@pytest.mark.django_db
def test_profile(client, settings, monkeypatch, mock_response) -> None:
    user = get_user_model()(username="pandichef")
    user.save()
    one_day_hence = timezone.now() + timedelta(days=1)
    AccessToken(user=user, token='secretstring', expires=one_day_hence, scope='read').save()
    response = client.get(reverse('djangito_server:profile'), **{'Authorization': f'Bearer secretstring'})
    assert response.status_code == 200
    json_response = response.content.decode('utf-8')
    assert json.loads(json_response)['username'] == 'pandichef'
