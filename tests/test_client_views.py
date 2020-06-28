import secrets
from urllib.parse import urlencode, urlparse

import pytest
import requests
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse

from djangito_client.views import login_handler


@pytest.fixture
def mock_response(monkeypatch):
    class MockResponse:
        text = """{"url": "mock_response"}"""
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: MockResponse())


@pytest.mark.django_db
def test_with_requestfactory(rf, settings, monkeypatch, mock_response) -> None:
    # imports
    monkeypatch.setattr(secrets, 'token_urlsafe', lambda: 'abcdefg')

    # inputs
    request = rf.get('', {'next': '/some_return_path'})  # note: path doesn't matter
    response = login_handler(request)

    # build response mantually
    redirect_uri = f"{request.scheme}://{request.get_host()}{reverse('callback_handler')}"
    oidc_url_as_dictionary = {
        'client_id': settings.DJANGITO_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'scope': 'read',
        'response_type': 'code',
        'response_mode': 'query',
        'nonce': secrets.token_urlsafe(),
        'state': '/some_return_path',
    }
    oidc_url = f'{settings.DJANGITO_SERVER_URL}/o/authorize?{urlencode(oidc_url_as_dictionary)}'
    response0 = HttpResponseRedirect(redirect_to=oidc_url)

    assert vars(response) == vars(response0)


@pytest.mark.django_db
def test_with_client(client, settings, monkeypatch, mock_response) -> None:
    # imports
    monkeypatch.setattr(secrets, 'token_urlsafe', lambda: 'abcdefg')

    # inputs
    response = client.get(reverse('login_handler'), {'next': '/some_return_path'})

    # build response mantually
    redirect_uri = f"http://testserver{reverse('callback_handler')}"
    oidc_url_as_dictionary = {
        'client_id': settings.DJANGITO_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'scope': 'read',
        'response_type': 'code',
        'response_mode': 'query',
        'nonce': secrets.token_urlsafe(),
        'state': '/some_return_path',
    }
    oidc_url = f'{settings.DJANGITO_SERVER_URL}/o/authorize?{urlencode(oidc_url_as_dictionary)}'
    response0 = HttpResponseRedirect(redirect_to=oidc_url)

    assert response.status_code == response0.status_code
    assert response.url == response0.url
