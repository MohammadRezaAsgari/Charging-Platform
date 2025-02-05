from rest_framework import status

from utils.api.error_objects import ErrorObject
from utils.api.responses import error_response


class BadRequestSerializerMixin:
    @staticmethod
    def serializer_error_response(
        serializer=None, error_object=None, extra_error_dict={}
    ):
        error_obj = {
            **(error_object or ErrorObject.BAD_REQUEST),
            "params": serializer.errors if serializer else {},
            **extra_error_dict,
        }
        return error_response(
            error=error_obj,
            status_code=status.HTTP_400_BAD_REQUEST,
            params=serializer.errors,
        )
