from urllib.parse import urlparse

from djangito_client.core import make_oidc_server_uri, make_postdict_to_fetch_token, extract_foreign_key_data


def test_make_oidc_server_uri() -> None:
    uri = make_oidc_server_uri(
        authorize_uri='http://127.0.0.1:8000/o/authorize',
        redirect_uri='https://oidcdebugger.com/debug',
        client_id='wCaCN31gF3kgI846ReFW8nXMcwPn6AvZ8lvWePEG',
        scope='read',
        state=None,
        nonce='p9ei0ifsvp')
    computed_by_oidcdebugger = """http://127.0.0.1:8000/o/authorize?client_id=wCaCN31gF3kgI846ReFW8nXMcwPn6AvZ8lvWePEG&redirect_uri=https%3A%2F%2Foidcdebugger.com%2Fdebug&scope=read&response_type=code&response_mode=query&nonce=p9ei0ifsvp"""
    assert str(urlparse(uri)) == str(urlparse(computed_by_oidcdebugger))  # urlparse reorders the GET parameters


def test_make_postdict_to_fetch_token() -> None:
    input = {"token_endpoint": "http://127.0.0.1:8000/o/token/",
             "grant_type": "authorization_code",
             "code": "xUEOXO0n6dKBursNgqHRSeGyq72TIz", "client_id": "id2",
             "client_secret": "secret2",
             "redirect_uri": "http://127.0.0.1:8001/oidc/callback_handler/"}
    result = make_postdict_to_fetch_token(**input)
    assert result == {"url": "http://127.0.0.1:8000/o/token/",
                      "data": {
                          "grant_type": "authorization_code",
                          "code": "xUEOXO0n6dKBursNgqHRSeGyq72TIz",
                          "client_id": "id2",
                          "client_secret": "secret2",
                          "redirect_uri": "http://127.0.0.1:8001/oidc/callback_handler/"
                      },
                      "headers": {"Content-Type": "application/x-www-form-urlencoded"}}



def test_extract_foreign_key_data() -> None:
    user_data = {'id': 1,
                 'company':
                     {
                         'id': 1,
                         'name': 'Jackson5',
                         'primary_activity': 2
                     },
                 'last_login': '2020-06-26T20:20:44.522017Z',
                 'is_superuser': True, 'username': 'pandichef',
                 'first_name': 'Michael', 'last_name': 'Jackson',
                 'email': 'mike@gmail.com', 'is_staff': True,
                 'is_active': True, 'date_joined': '2020-06-07T20:06:32Z'
                 }
    string_data, foreign_key_data = extract_foreign_key_data(user_data)
    assert string_data == {"date_joined": "2020-06-07T20:06:32Z",
                           "is_superuser": True, "last_name": "Jackson",
                           "last_login": "2020-06-26T20:20:44.522017Z",
                           "username": "pandichef", "first_name": "Michael",
                           "is_staff": True, "is_active": True,
                           "email": "mike@gmail.com", "server_id": 1}
    assert foreign_key_data == {"company": {"name": "Jackson5", "primary_activity": 2, "server_id": 1}}
