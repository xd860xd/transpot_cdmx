from rest_framework import exceptions


class BadGateWay(exceptions.APIException):

    status_code = 502
    default_detail = "Service temporarily unavailable, try again later."
    default_code = "service_unavailable"
