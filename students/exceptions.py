import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    ValidationError,
    NotFound,
)
from django.http import Http404

logger = logging.getLogger(__name__)


class StudentNotFoundException(APIException):
    """
    Custom exception raised when a requested student is not found.
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'STUDENT_NOT_FOUND'

    def __init__(self, student_id=None):
        if student_id is not None:
            self.student_id = student_id
            detail = f"Student with ID {student_id} not found."
        else:
            self.student_id = None
            detail = "Student not found."
        super().__init__(detail=detail, code=self.default_code)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework.
    Standardizes error responses into a consistent JSON envelope:

    {
        "success": false,
        "error": {
            "code": "...",
            "message": "...",
            "details": { ... }  # Included for validation errors
        }
    }
    """
    # Normalize Django Http404 to DRF NotFound
    if isinstance(exc, Http404):
        exc = NotFound(*(exc.args))

    # Call REST framework's default exception handler to get standard response
    response = exception_handler(exc, context)

    # 1. Handle unexpected 500 Server Errors (when DRF returns None)
    if response is None:
        logger.error(f"Unhandled server error occurred: {exc}", exc_info=True)
        return Response(
            {
                "success": False,
                "error": {
                    "code": "SERVER_ERROR",
                    "message": "An unexpected server error occurred."
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # 2. Handle missing student (404)
    if isinstance(exc, StudentNotFoundException):
        response.data = {
            "success": False,
            "error": {
                "code": "STUDENT_NOT_FOUND",
                "message": str(exc.detail)
            }
        }
        return response

    # 3. Handle validation errors (400)
    if isinstance(exc, ValidationError):
        response.data = {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid student data.",
                "details": response.data
            }
        }
        return response

    # 4. Handle generic 404 Not Found (e.g. invalid pagination page)
    if isinstance(exc, NotFound) or response.status_code == status.HTTP_404_NOT_FOUND:
        detail_msg = response.data.get('detail', 'Resource not found.') if isinstance(response.data, dict) else str(response.data)
        response.data = {
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": detail_msg
            }
        }
        return response

    # 5. Handle any other client/API errors (401, 403, 405, etc.)
    detail_msg = response.data.get('detail', 'A client error occurred.') if isinstance(response.data, dict) else str(response.data)
    error_code = getattr(exc, 'default_code', 'CLIENT_ERROR').upper()
    response.data = {
        "success": False,
        "error": {
            "code": error_code,
            "message": detail_msg
        }
    }
    return response
