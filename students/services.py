from django.db.models import Q
from .models import Student


class StudentService:
    """
    Service Layer encapsulating all business logic, queries, and data
    manipulation for the Student domain. Decouples API views from the ORM.
    """

    def list_students(self, department=None, course=None, year=None, search=None, ordering=None):
        """
        Query students with optional filtering, search, and ordering.
        """
        students = Student.objects.all()

        # Step 17: Filtering
        if department:
            students = students.filter(department__iexact=department)

        if course:
            students = students.filter(course__iexact=course)

        if year is not None:
            students = students.filter(year=year)

        # Step 18: Search
        if search:
            students = students.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(student_id__icontains=search)
            )

        # Step 19: Ordering
        if ordering:
            ordering_fields = [f.strip() for f in ordering.split(',') if f.strip()]
            valid_fields = []
            model_fields = {f.name for f in Student._meta.get_fields()}
            for field in ordering_fields:
                clean_field = field.lstrip('-+')
                if clean_field in model_fields:
                    valid_fields.append(field)
            if valid_fields:
                students = students.order_by(*valid_fields)
            else:
                students = students.order_by('id')
        else:
            students = students.order_by('id')

        return students

    def get_student_by_id(self, student_id):
        """
        Retrieve a single student by primary key ID or return None.
        """
        try:
            return Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return None

    def create_student(self, validated_data):
        """
        Create and persist a new Student record from validated schema data.
        """
        return Student.objects.create(**validated_data)

    def update_student(self, student, validated_data):
        """
        Update an existing student record with validated data.
        """
        for field, value in validated_data.items():
            setattr(student, field, value)
        student.save()
        return student

    def delete_student(self, student):
        """
        Delete a student record from the database.
        """
        student.delete()
        return True
