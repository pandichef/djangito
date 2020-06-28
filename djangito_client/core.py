# "core.py" contains pure functions i.e., no side effects
from typing import Optional
from urllib.parse import urlencode


def make_oidc_server_uri(authorize_uri: str, redirect_uri: str, client_id: str,
                         scope: str, state: Optional[str],
                         nonce: Optional[str],
                         response_type: str = 'code',
                         response_mode: str = 'query') -> str:
    """
    Args:
        authorize_uri: (required) The authorize URI on the authorization server
            is where an OpenID Connect flow starts.
        redirect_uri: (required) The redirect URI tells the issuer where to redirect
            the browser back to when the flow is done.
        client_id:  (required) Every client (website or mobile app) is identified
            by a client ID. Unlike a client secret, the client ID is a public value
            that does not have to be protected.
        scope: (required) Clients can request additional information or permissions
            via scopes.  The OpenID Connect spec defines some standard scopes,
            and applications can define their own custom scopes as well.
        state: The state is an optional value that is carried through the whole
            flow and returned to the client.  It's common to use state to store an a
            nti-forgery token that can be verified after the login flow is complete.
            Another common use is storing the location the user should be redirected to after logging in.
        nonce: A nonce (or number used once) is a random value that is used to
            prevent replay attacks.
        response_type: (required) If "code", the authorization server will
            respond with a code, which the client can exchange for tokens on a
            secure channel. This flow should be used when the application code
            runs on a secure server (common for MVC and server-rendered pages apps).
        response_mode: (required) The desired http method for the response e.g., query,
        form_post, fragment

    Returns: URI string for browser redirect to Authorization Server

    References:
        https://oidcdebugger.com/
        https://openid.net/specs/openid-connect-core-1_0.html#ScopeClaims
    """
    oidc_url_as_dictionary = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'response_type': response_type,
        'response_mode': response_mode,
        'nonce': nonce,
        'state': state,
    }
    if not state:
        del oidc_url_as_dictionary['state']
    if not nonce:
        del oidc_url_as_dictionary['nonce']
    return f'{authorize_uri}?{urlencode(oidc_url_as_dictionary)}'


def make_postdict_to_fetch_token(token_endpoint: str, grant_type: str,
                                 code: str, client_id: str,
                                 client_secret: str,
                                 redirect_uri: str) -> dict:
    """POST dictionary is the API of the requests library"""
    return {'url': token_endpoint,
            'data': {
                'grant_type': grant_type,
                'code': code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
            },
            'headers': {
                'Content-Type': 'application/x-www-form-urlencoded',
            }}


def extract_foreign_key_data(user_data):
    foreign_key_list = []
    for x in user_data:
        if type(user_data[x]) == dict:
            foreign_key_list.append(x)

    string_data = {x: user_data[x] for x in
                   set(user_data) - set(foreign_key_list)}
    foreign_key_data = {x: user_data[x] for x in foreign_key_list}
    string_data['server_id'] = string_data['id']
    del string_data['id']
    for x in foreign_key_data:
        foreign_key_data[x]['server_id'] = foreign_key_data[x]['id']
        del foreign_key_data[x]['id']
    return string_data, foreign_key_data
