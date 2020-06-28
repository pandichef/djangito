import json

from django.contrib.auth import get_user_model
from django.http import HttpResponse

from oauth2_provider.decorators import protected_resource

from .serializers import get_user_serializer

User = get_user_model()
# Company = User._meta.get_field('company').remote_field.model
UserSerializer = get_user_serializer(User)


# @protected_resource(scopes=['openid email'])
@protected_resource(scopes=['read'])
def profile(request):
    """Serves the user's profile; ForeignKey fields as served as nested dictionaries"""
    # uses the Google API cf. https://developers.google.com/identity/protocols/OpenIDConnect
    user_dict = UserSerializer(request.resource_owner).data
    user_serialized = json.dumps(user_dict)
    return HttpResponse(user_serialized, content_type="application/json")


def get_admin_url(request):
    """This is used to create the password_change view on the djangito client admin"""
    from django.shortcuts import reverse
    thisjson = {
        "url": reverse('admin:password_change'),
    }
    return HttpResponse(json.dumps(thisjson), content_type="application/json")
