from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler to ensure consistent error response format
    """
    response = exception_handler(exc, context)

    if response is not None:
        if response.status_code == 404:
            if isinstance(response.data, dict):
                if 'detail' in response.data:
                    error_message = response.data.get('detail')
                    if isinstance(error_message, dict) and 'error' in error_message:
                        response.data = error_message
                    else:
                        response.data = {'error': str(error_message)}
                elif 'error' not in response.data:
                    response.data = {'error': 'Not found'}
        
        if 'error' not in response.data and 'detail' in response.data:
            response.data = {'error': str(response.data['detail'])}

    return response