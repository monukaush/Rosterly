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
    if isinstance(exc, Http404):
        exc = NotFound(*(exc.args))

    response = exception_handler(exc, context)

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

    if isinstance(exc, StudentNotFoundException):
        response.data = {
            "success": False,
            "error": {
                "code": "STUDENT_NOT_FOUND",
                "message": str(exc.detail)
            }
        }
        return response

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