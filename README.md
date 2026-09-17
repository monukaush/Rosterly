# Rosterly - Student Management REST API

Rosterly is a Student Management REST API built using Django REST Framework and MySQL. It provides APIs for managing student records with CRUD operations, data validation, filtering, searching, ordering, pagination, custom error handling, Swagger/OpenAPI documentation, and automated testing with Pytest.

## Features

- Student CRUD operations
- Serializer-based data validation
- Student filtering by department, course, and year
- Student search
- Ordering and sorting
- Pagination
- Service layer for reusable business logic
- Custom exception handling
- Structured API error responses
- Swagger/OpenAPI documentation
- Automated testing with Pytest
- 96% test coverage

## Tech Stack

- Python
- Django
- Django REST Framework
- MySQL
- Pytest
- pytest-django
- pytest-cov
- drf-spectacular
- Swagger/OpenAPI

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/students/` | Get all students |
| POST | `/api/students/` | Create a student |
| GET | `/api/students/{id}/` | Get a student by ID |
| PUT | `/api/students/{id}/` | Update a student |
| PATCH | `/api/students/{id}/` | Partially update a student |
| DELETE | `/api/students/{id}/` | Delete a student |

## Filtering

Students can be filtered using query parameters.

### Filter by Department and Year

```text
GET /api/students/?department=CSE&year=4
```

This returns students belonging to the CSE department and academic year 4.

### Search

```text
GET /api/students/?search=Rahul
```

### Ordering

Ascending order:

```text
GET /api/students/?ordering=age
```

Descending order:

```text
GET /api/students/?ordering=-age
```

### Pagination

```text
GET /api/students/?page=1&page_size=10
```

## Student Data Example

```json
{
    "first_name": "Rahul",
    "last_name": "Sharma",
    "age": 22,
    "email": "rahul@example.com",
    "phone": "9876543211",
    "date_of_birth": "2003-05-10",
    "course": "B.Tech",
    "department": "CSE",
    "year": 4,
    "student_id": "STU3001",
    "address": "Delhi, India"
}
```

## Swagger / OpenAPI

Swagger UI provides interactive documentation for all available API endpoints.

Swagger URL:

```text
http://127.0.0.1:8000/api/docs/
```

From Swagger UI, you can test:

- GET all students
- POST a new student
- GET student by ID
- PUT student
- PATCH student
- DELETE student

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/monukaush/Rosterly.git
cd Rosterly
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

For Windows:

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root and add the required Django and database configuration.

Do not upload the `.env` file to GitHub.

### 6. Apply migrations

```bash
python manage.py migrate
```

### 7. Run the development server

```bash
python manage.py runserver
```

API:

```text
http://127.0.0.1:8000/
```

Swagger:

```text
http://127.0.0.1:8000/api/docs/
```

## Testing

Run all automated tests:

```bash
pytest
```

Current test result:

```text
41 passed
```

## Test Coverage

Generate the coverage report:

```bash
pytest --cov=students --cov-report=term-missing
```

Current test coverage:

```text
96%
```

## Error Handling

The API provides structured error responses for validation errors and resources that are not found.

Example:

```json
{
    "success": false,
    "error": {
        "code": "STUDENT_NOT_FOUND",
        "message": "Student with ID 99999 not found."
    }
}
```

## Project Structure

```text
Rosterly/
│
├── manage.py
├── pytest.ini
├── README.md
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
└── students/
    ├── migrations/
    ├── admin.py
    ├── apps.py
    ├── exceptions.py
    ├── models.py
    ├── serializers.py
    ├── services.py
    ├── tests.py
    ├── urls.py
    └── views.py
```

## Future Improvements

- JWT authentication
- Role-based access control
- Production deployment
- Frontend integration
- API rate limiting

## License

This project is for educational and development purposes.