from rest_framework import permissions


def is_read_request(request):
    return request.method in permissions.SAFE_METHODS


def is_write_request(request):
    return not is_read_request(request)
