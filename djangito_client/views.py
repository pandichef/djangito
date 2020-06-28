import json
import logging
import secrets

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import HttpResponse, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import jwt
from djangito_client import core, io

logger = logging.getLogger(__name__)

# This was needed for whatever reason
DJANGITO_SERVER_URL = settings.DJANGITO_SERVER_URL
DJANGITO_CLIENT_ID = settings.DJANGITO_CLIENT_ID
DJANGITO_CLIENT_SECRET = settings.DJANGITO_CLIENT_SECRET


@require_http_methods(['GET'])
def login_handler(request) -> HttpResponse:
    """
    Args:
        request.GET['next']: Produced by Django, this is the redirect path

    Returns: HttpResponseRedirect to the server URL

    Notes:
        Pytest x: rf.get('', {'next': '/some_return_path'})
        Pytest y: HttpResponseRedirect(redirect_to=server_url_with_oauth2_params)
    """
    nonce = secrets.token_urlsafe()
    """Redirects to OpenID Connect Authorization Server"""
    the_original_path = request.GET['next']
    redirect_uri = f"{request.scheme}://{request.get_host()}{reverse('callback_handler')}"
    oidc_url_as_dictionary2 = {
        'authorize_uri': f"{DJANGITO_SERVER_URL}/o/authorize",
        'client_id': DJANGITO_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'scope': 'read',
        'nonce': nonce,
        'state': the_original_path,
    }
    oidc_url2 = core.make_oidc_server_uri(**oidc_url_as_dictionary2)
    return redirect(oidc_url2)


@require_http_methods(['GET'])
def callback_handler(request) -> HttpResponse:
    """
    Args:
        request.GET['state']: The redirect path
        request.GET['code']: The oauth2 authorization code

    Returns: HttpResponseRedirect back to the original URL stored in the state parameter

    Notes:
        Pytest x: rf.get('', {'next': '/some_return_path', 'code': 'some_code'})
        Pytest y: HttpResponseRedirect(redirect_to=the_original_url)
    """
    try:
        # collect query string params from the OIDC redirect
        the_original_path = request.GET['state']  # This is the redirect path
        authorization_code = request.GET['code']
        redirect_uri = f"{request.scheme}://{request.get_host()}{reverse('callback_handler')}"

        # [1] Use authorization code to get token via the back channel
        # This is typically handled with a POST; I switched it to a GET to
        # circumvent a connection issue on PythonAnywhere with free accounts
        token_postdict = core.make_postdict_to_fetch_token(**{
            'token_endpoint': f'{DJANGITO_SERVER_URL}/o/token/',
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'client_id': DJANGITO_CLIENT_ID,
            'client_secret': DJANGITO_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
        })

        res = requests.post(**token_postdict)
        res_dict = res.json()
        access_token = res_dict['access_token']

        # [2] Use the token to get user data
        res = requests.get(f'{DJANGITO_SERVER_URL}/o/profile/', headers={
            'Authorization': f'Bearer {access_token}',
        })
        user_data = res.json()

        string_data, foreign_key_data = core.extract_foreign_key_data(user_data)
        user = io.save_user_string_fields(string_data)
        io.save_user_foreign_key_fields(foreign_key_data, user)
        login(request, user)

        return redirect(the_original_path)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        print("SSO login failed.  Redirecting to admin:login")
        messages.info(request, 'SSO authentication failed.  Redirecting to site login.')
        return redirect('admin:login')


@require_http_methods(['POST'])
@csrf_exempt
def push_server_data_to_client(request) -> HttpResponse:
    from jwt.exceptions import InvalidSignatureError
    try:
        user_data = jwt.decode(request.POST['token'], DJANGITO_CLIENT_SECRET, algorithms=['HS256'])
        string_data, foreign_key_data = core.extract_foreign_key_data(user_data)
        user = io.save_user_string_fields(string_data)
        io.save_user_foreign_key_fields(foreign_key_data, user)
        return HttpResponse(f'User profile updated on {request.scheme}://{request.get_host()} (client ID: {DJANGITO_CLIENT_ID}).')
    except InvalidSignatureError as e:
        error_message = f"Attempt to refresh user data on {request.build_absolute_uri()} failed.  The Djangito application client ID and/or secret may be out of sync."
        logger.warning(error_message)
        from django.http import HttpResponseServerError
        return HttpResponseServerError(error_message)
