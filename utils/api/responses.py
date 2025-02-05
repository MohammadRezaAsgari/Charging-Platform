from rest_framework import status
from rest_framework.response import Response


def success_response(data: dict, status_code: int = status.HTTP_200_OK) -> Response:
    response_data = {
        "success": True,
        "data": data,
    }
    return Response(response_data, status_code)


def error_response(
    error: dict, status_code: int = status.HTTP_400_BAD_REQUEST, params=None
) -> Response:
    if params is None:
        params = {}
    # params is a dictionary of additional parameters to be added to the error object
    response_data = {
        "success": False,
        "error": {
            **error,
            "params": params,
        },
    }
    return Response(response_data, status_code)
