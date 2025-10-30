from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework import exceptions as drf_exceptions
from django.http import Http404

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    if isinstance(exc, drf_exceptions.ValidationError):
        response.data = {
            'error': 'Validation failed',
            'details': response.data
        }
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response

    if isinstance(exc, Http404) or getattr(exc, 'status_code', None) == status.HTTP_404_NOT_FOUND:
        detail = response.data.get('detail') if isinstance(response.data, dict) else None
        if detail and 'country' in str(detail).lower():
            response.data = {'error': 'Country not found'}
        else:
            response.data = {'error': detail or 'Not found'}
        response.status_code = status.HTTP_404_NOT_FOUND
        return response

    return response