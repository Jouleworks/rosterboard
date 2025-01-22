from django.conf import settings # import the settings file
from django.http.request import HttpRequest


def get_domain(request: HttpRequest):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'DOMAIN': request.get_host()}