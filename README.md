# Djangito
Enables one Django project (client) to authenticate via a second Django project 
(server) via [oauth2](https://oauth.net/2/).

### Why is this better than than a giant project with different apps?
* When apps aren't bundled in a single Django project, [settings.py](https://docs.djangoproject.com/en/dev/topics/settings/) 
becomes easier to maintain.  Moreover, you can customize settings.py for each app without 
having to resort to hacks.
* You can run the entire test suite quickly.
* Your apps can use [different SQL databases](https://docs.djangoproject.com/en/dev/ref/databases/) e.g., SQLite, Postgres.
* You can easily incorporate apps written in other web frameworks like [Flask](https://flask.palletsprojects.com/en/master/), 
[Express.js](https://expressjs.com/), or [Rails](https://rubyonrails.org/).
* You can easily support [SSO](https://en.wikipedia.org/wiki/Single_sign-on) for 
3rd party software that you acquire.
* You can quickly build a prototype of a new app without having to worry about 
deprecating it at some point.
* You can hire freelancers to help develop one app without having to share your 
entire code base.
* You can trial new deployment strategies on one app at a time (e.g., your main 
Django project is on [Heroku](https://www.heroku.com/) while you beta test a new 
app using [Zappa](https://github.com/Miserlou/Zappa)).

Djangito can also be used as an alternative to an SSO service (e.g., [AWS Cognito](https://aws.amazon.com/cognito/)). But
 it's cheaper, fully customizable, and seamlessly handles 
[foreign key relationships](https://docs.djangoproject.com/en/dev/topics/db/examples/many_to_one/) 
with [custom User tables](https://docs.djangoproject.com/en/dev/topics/auth/customizing/#substituting-a-custom-user-model).

### Server Installation
1. `pip install djangito`  # in server virtual environment  
1. Add `oauth2_provider` and `django_server` to INSTALLED_APPS in settings.py  
1. Add `users` to INSTALLED_APPS and `AUTH_USER_MODEL = 'users.User'` in settings.py
(only required if you want to use the [opinionated Djangito user model](https://github.com/pandichef/djangito/blob/master/users/models.py))
1. Add `path('o/', include('djangito_server.urls'))` to urls.py
1. Create an [OAuth2 Client Application](https://django-oauth-toolkit.readthedocs.io/en/latest/tutorial/tutorial_01.html#create-an-oauth2-client-application) 
in the [Django admin](https://docs.djangoproject.com/en/dev/ref/contrib/admin/) 
with parameters `client_type="confidential"` and `authorization_grant_type="authorization-code"`. 
`skip_authorization` can also be set to `True` to bypass the page asking users to 
grant authority to the client application.

_Note: While this project uses [DRF serializers](https://www.django-rest-framework.org/api-guide/serializers/), 
`rest_framework` does not need to be install as a Django app in your project._

### Client Installation
1. `pip install djangito`  # in client virtual environment  
1. Add `'django_client'` to INSTALLED_APPS in settings.py
1. Add `'users'` to INSTALLED_APPS and `AUTH_USER_MODEL = 'users.User'` in settings.py
(only required if you want to use the opinionated Djangito user model)
1. Add `path('oidc/', include('djangito_client.urls'))` to urls.py
1. Create an Application on *server admin* in instance to get `DJANGITO_CLIENT_ID` AND `DJANGITO_CLIENT_SECRET`
1. Add Djangito settings to [settings.py](https://docs.djangoproject.com/en/dev/topics/settings/) e.g.,
```python
DJANGITO_SERVER_URL = 'https://main.mysite.com'
DJANGITO_CLIENT_ID = 'some_large_string_generated_by_djangito_server_app'
DJANGITO_CLIENT_SECRET = 'another_large_string_generated_by_djangito_server_app'
```

### Features
* Client application redirects user login to server application
* Client pulls that user's data using oauth2 after logging in ("authorization code" flow)
* Client will also update all foreign key fields (e.g., `user.company`), 
_including_ the data associated with that ForeignKey
* When user data changes on the server, it is POSTed to *all* the client applications 
via a JWT (signed using `DJANGITO_CLIENT_SECRET`)
* If server User data is deleted, there is (currently) no impact to the client User data
* Comes with an opinionated "[users](https://github.com/pandichef/djangito/tree/master/users)" 
app containing a [custom User model](https://github.com/pandichef/djangito/blob/master/users/models.py). 
(You can create your own user model as well.  Just add an Integer field called server_id to your custom User model as well as 
to all related ForeignKey fields.  You can also modify the Djangito User model 
by just copying the "user" directory into your project directory and 
[the local version will be used](https://docs.python.org/3/tutorial/modules.html#the-module-search-path).)

_Note: "users" wasn't named "djangito_users" since, per the Django documentation,
[settings.AUTH_USER_MODEL can't change mid-project](https://docs.djangoproject.com/en/3.0/ref/settings/#auth-user-model). 
The name "users" is commonly used in tutorials for a custom User model 
(e.g., [how-switch-custom-django-user-model-mid-project](https://www.caktusgroup.com/blog/2019/04/26/how-switch-custom-django-user-model-mid-project/))._

### When is data synced?
1. Anytime the user logs in from the client application
1. Anytime the data is modified on the server application (note that just logging 
into the server application modifies the last_login field)

### How logging in works?
1. [settings.LOGIN_URL is monkey patched](https://github.com/pandichef/djangito/blob/c4a52be47845793cbc0161929bc1ea4f75431768/djangito_client/patches.py#L38) 
in [djangito_client.patches](https://github.com/pandichef/djangito/blob/master/djangito_client/patches.py) 
to redirect to client.com/login_handler
1. login_handler directs to server.com/o/authorize with query string parameters 
client_id, redirect_uri, scope (i.e., permissions requested), nonce, the original 
path that initiated the transaction.
1. server.com/o/authorize (oauth2_provider.AuthorizationView) executes authorization 
and redirects to callback URI with query string parameters authorization, the original 
that initiated the transaction
1. callback_handler gets access token
1. callback_handler gets user_data from server using the access token
1. callback_handler creates (or updates) User table using the JSON user data from 
the server.
1. callback_handler create a random password for the client database i.e., just a fill
to avoid exceptions.
1. callback_handler calls login(request, u) to login user
1. callback_handler revokes the token on the server i.e., this simulate one-time-use
1. callback_handler redirects back to the original URL, now authenticated

### How logging out works?
1. [settings.LOGIN_REDIRECT_URL is monkey patched](https://github.com/pandichef/djangito/blob/c4a52be47845793cbc0161929bc1ea4f75431768/djangito_client/patches.py#L36) 
in [djangito_client.patches](https://github.com/pandichef/djangito/blob/master/djangito_client/patches.py) to redirect to server.com/o/logout
1. server.com/o/logout calls logout(request)
1. server.com/o/logout redirects to client.com

### References
* [The blog post that inspired this project](https://raphaelyancey.fr/en/2018/05/28/setting-up-django-oauth2-server-client.html)  
* [The best video explaining OpenID Connect](https://www.youtube.com/watch?v=996OiexHze0&list=LLvwEyJhl-YPSJRMV0fuE5kg)  
* [Setting up an OAuth Client using authlib](https://docs.authlib.org/en/latest/client/django.html)  
* [django-simple-sso](https://github.com/divio/django-simple-sso) (I couldn't get this to work, but the idea is very similar)
* [The blog post that inspired the use of pytest in this project](https://djangostars.com/blog/django-pytest-testing/)

### Testing Utilities
* [https://oidcdebugger.com/](https://oidcdebugger.com/)  
* [https://oauthdebugger.com/](https://oauthdebugger.com/)
