from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
)

from .serializers import StudentSerializer
from .services import StudentService
from .exceptions import StudentNotFoundException


student_service = StudentService()


class StudentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema_view(
    get=extend_schema(
        summary="Get all students",
        description=(
            "Returns a list of students with filtering, "
            "search, ordering and pagination."
        ),
        parameters=[
            OpenApiParameter(
                name="department",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter students by department.",
            ),
            OpenApiParameter(
                name="course",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter students by course.",
            ),
            OpenApiParameter(
                name="year",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Filter students by academic year.",
            ),
            OpenApiParameter(
                name="search",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Search students.",
            ),
            OpenApiParameter(
                name="ordering",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Order students, e.g. age or -age.",
            ),
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Page number.",
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Number of students per page.",
            ),
        ],
        responses={200: StudentSerializer(many=True)},
    ),
    post=extend_schema(
        summary="Create a student",
        description="Creates a new student after validating the request data.",
        request=StudentSerializer,
        responses={
            201: StudentSerializer,
            400: None,
        },
    ),
)
@api_view(['GET', 'POST'])
def student_list(request, service=student_service):
    if request.method == 'GET':
        department = request.query_params.get('department')
        course = request.query_params.get('course')
        year = request.query_params.get('year')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')

        parsed_year = None
        if year:
            try:
                parsed_year = int(year)
            except ValueError:
                raise ValidationError({
                    'year': [
                        'Invalid year format. Year must be an integer.'
                    ]
                })

        students = service.list_students(
            department=department,
            course=course,
            year=parsed_year,
            search=search,
            ordering=ordering
        )

        paginator = StudentPagination()
        paginated_students = paginator.paginate_queryset(
            students,
            request
        )

        if paginated_students is not None:
            serializer = StudentSerializer(
                paginated_students,
                many=True
            )
            return paginator.get_paginated_response(
                serializer.data
            )

        serializer = StudentSerializer(
            students,
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    elif request.method == 'POST':
        serializer = StudentSerializer(
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )
        student = service.create_student(
            serializer.validated_data
        )
        return Response(
            StudentSerializer(student).data,
            status=status.HTTP_201_CREATED
        )


@extend_schema_view(
    get=extend_schema(
        summary="Get student by ID",
        description="Returns a single student using the student ID.",
        responses={
            200: StudentSerializer,
            404: None,
        },
    ),
    put=extend_schema(
        summary="Update student",
        description="Completely updates an existing student.",
        request=StudentSerializer,
        responses={
            200: StudentSerializer,
            400: None,
            404: None,
        },
    ),
    patch=extend_schema(
        summary="Partially update student",
        description="Updates selected fields of an existing student.",
        request=StudentSerializer,
        responses={
            200: StudentSerializer,
            400: None,
            404: None,
        },
    ),
    delete=extend_schema(
        summary="Delete student",
        description="Deletes an existing student.",
        responses={
            204: None,
            404: None,
        },
    ),
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def student_detail(request, id, service=student_service):
    student = service.get_student_by_id(id)
    if not student:
        raise StudentNotFoundException(
            student_id=id
        )

    if request.method == 'GET':
        serializer = StudentSerializer(student)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    elif request.method == 'PUT':
        serializer = StudentSerializer(
            student,
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )
        updated_student = service.update_student(
            student,
            serializer.validated_data
        )
        return Response(
            StudentSerializer(updated_student).data,
            status=status.HTTP_200_OK
        )

    elif request.method == 'PATCH':
        serializer = StudentSerializer(
            student,
            data=request.data,
            partial=True
        )
        serializer.is_valid(
            raise_exception=True
        )
        updated_student = service.update_student(
            student,
            serializer.validated_data
        )
        return Response(
            StudentSerializer(updated_student).data,
            status=status.HTTP_200_OK
        )

    elif request.method == 'DELETE':
        service.delete_student(student)
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )