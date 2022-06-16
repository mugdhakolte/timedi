import datetime

from django.utils.crypto import get_random_string
from rest_framework.views import exception_handler
from rest_framework.renderers import JSONRenderer
from django.utils.translation import ugettext_lazy as _

from timedi_auth.models import Token
from timedi_auth.custom_responses import custom_responses


def create_token(user, action):
    """To create random token in database."""

    token = get_random_string(length=32)

    expires_at = datetime.datetime.now() + datetime.timedelta(days=1)

    token = Token.objects.create(
        user=user, action=action, token=token,
        expires_at=expires_at,

    )
    return token


class CustomJSONRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data, dict) and "status_code" in data.keys():
            data = data
        else:
            data = {'data': data}
            request = renderer_context["request"]
            response = renderer_context["response"]
            if request.method == "POST":
                custom_response_dict = custom_responses.get(request.path.rsplit("/")[-2])
                if custom_response_dict:
                    response_message = custom_response_dict.get(response.status_code)
                    if response_message:
                        data["message"] = str(response_message)

                    # else:
                    #     data["message"] = _("Please correct the errors below.")

            elif request.method in ["PUT", "PATCH"]:
                custom_response_dict = custom_responses.get(request.path.rsplit("/")[-3])
                if custom_response_dict:
                    response_message = custom_response_dict.get(response.status_code)
                    if response_message:
                        data["message"] = str(response_message)
                    # else:
                    #     data["message"] = _("Please correct the errors below.")

            elif request.method == "DELETE":
                custom_response_dict = custom_responses.get(request.path.rsplit("/")[-3])
                if custom_response_dict:
                    response_message = custom_response_dict.get(response.status_code)
                    if response_message:
                        data = {"message": str(response_message)}
                        response.status_code = 200
                    # else:
                    #     data["message"] = _("Please correct the errors below.")
        return super(CustomJSONRenderer, self).render(data, accepted_media_type, renderer_context)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None and isinstance(response.data, dict):
        custom_data = response.data
        if "detail" in response.data.keys() and response.status_code in [401, 403, 500]:
            custom_data["status_code"] = response.status_code
            custom_data["message"] = response.data.get("detail", None)
        else:
            custom_data["message"] = _("Please correct the errors below.")
        response.data = custom_data

    return response
