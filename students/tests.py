from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Student
from .services import StudentService


class StudentDetailAPITests(APITestCase):

    def setUp(self):
        self.student = Student.objects.create(
            first_name="Rahul",
            last_name="Kumar",
            age=21,
            email="rahul@example.com",
            phone="9876543210",
            date_of_birth="2003-01-15",
            course="B.Tech",
            department="CSE",
            year=3,
            student_id="STU1001",
            address="New Delhi, India"
        )
        self.detail_url = reverse('student-detail', kwargs={'id': self.student.id})
        self.not_found_url = reverse('student-detail', kwargs={'id': 99999})

    def test_get_student_by_id_success(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], "Rahul")
        self.assertEqual(response.data['email'], "rahul@example.com")

    def test_get_student_by_id_not_found(self):
        response = self.client.get(self.not_found_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_put_update_student_success(self):
        payload = {
            "first_name": "Rahul",
            "last_name": "Sharma",
            "age": 22,
            "email": "rahul.sharma@example.com",
            "phone": "9876543211",
            "date_of_birth": "2003-01-15",
            "course": "B.Tech",
            "department": "IT",
            "year": 4,
            "student_id": "STU1001",
            "address": "Noida, India"
        }
        response = self.client.put(self.detail_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertEqual(self.student.last_name, "Sharma")
        self.assertEqual(self.student.age, 22)
        self.assertEqual(self.student.department, "IT")

    def test_put_update_student_validation_failure(self):
        payload = {
            "first_name": "Rahul"
        }
        response = self.client.put(self.detail_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_partial_update_student_success(self):
        payload = {
            "phone": "9999988888",
            "address": "Gurugram, India"
        }
        response = self.client.patch(self.detail_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertEqual(self.student.phone, "9999988888")
        self.assertEqual(self.student.address, "Gurugram, India")
        self.assertEqual(self.student.first_name, "Rahul")

    def test_delete_student_success(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Student.objects.filter(id=self.student.id).exists())

    def test_delete_student_not_found(self):
        response = self.client.delete(self.not_found_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class StudentFilteringAndSearchAPITests(APITestCase):

    def setUp(self):
        self.list_url = reverse('student-list')
        self.s1 = Student.objects.create(
            first_name="Rahul",
            last_name="Sharma",
            age=22,
            email="rahul.sharma@example.com",
            phone="9876543210",
            date_of_birth="2002-01-15",
            course="B.Tech",
            department="CSE",
            year=4,
            student_id="STU1001",
            address="Delhi"
        )
        self.s2 = Student.objects.create(
            first_name="Priya",
            last_name="Patel",
            age=21,
            email="priya.patel@example.com",
            phone="9876543211",
            date_of_birth="2003-05-20",
            course="B.Tech",
            department="ECE",
            year=3,
            student_id="STU1002",
            address="Mumbai"
        )
        self.s3 = Student.objects.create(
            first_name="Amit",
            last_name="Verma",
            age=23,
            email="amit.verma@example.com",
            phone="9876543212",
            date_of_birth="2001-11-10",
            course="MCA",
            department="CSE",
            year=1,
            student_id="STU1003",
            address="Noida"
        )
        self.s4 = Student.objects.create(
            first_name="Neha",
            last_name="Singh",
            age=22,
            email="neha.singh@example.com",
            phone="9876543213",
            date_of_birth="2002-09-05",
            course="B.Tech",
            department="IT",
            year=4,
            student_id="STU1004",
            address="Gurugram"
        )

    def get_results(self, response):
        if isinstance(response.data, dict) and 'results' in response.data:
            return response.data['results']
        return response.data

    def test_filter_by_department(self):
        response = self.client.get(self.list_url, {'department': 'CSE'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_results(response)
        self.assertEqual(len(results), 2)
        ids = [s['student_id'] for s in results]
        self.assertIn("STU1001", ids)
        self.assertIn("STU1003", ids)

    def test_filter_by_year(self):
        response = self.client.get(self.list_url, {'year': 4})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_results(response)
        self.assertEqual(len(results), 2)
        ids = [s['student_id'] for s in results]
        self.assertIn("STU1001", ids)
        self.assertIn("STU1004", ids)

    def test_filter_by_course(self):
        response = self.client.get(self.list_url, {'course': 'MCA'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_results(response)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['student_id'], "STU1003")

    def test_filter_combined_department_and_year(self):
        response = self.client.get(self.list_url, {'department': 'CSE', 'year': 4})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_results(response)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['student_id'], "STU1001")

    def test_filter_invalid_year_returns_400(self):
        response = self.client.get(self.list_url, {'year': 'abc'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_search_by_first_name(self):
        response = self.client.get(self.list_url, {'search': 'Rahul'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_results(response)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['first_name'], "Rahul")

    def test_search_by_last_name(self):
        response = self.client.get(self.list_url, {'search': 'Singh'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_results(response)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['last_name'], "Singh")

    def test_search_by_email(self):
        response = self.client.get(self.list_url, {'search': 'priya.patel'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_results(response)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['student_id'], "STU1002")

    def test_search_by_student_id(self):
        response = self.client.get(self.list_url, {'search': 'STU1003'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_results(response)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['first_name'], "Amit")

    def test_search_case_insensitive(self):
        response = self.client.get(self.list_url, {'search': 'rahul'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_results(response)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['first_name'], "Rahul")

    def test_search_and_filter_combined(self):
        response = self.client.get(self.list_url, {'search': 'Verma', 'department': 'CSE'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_results(response)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['student_id'], "STU1003")

    def test_search_no_match_returns_empty_list(self):
        response = self.client.get(self.list_url, {'search': 'NonExistentPerson'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_results(response)
        self.assertEqual(len(results), 0)

    def test_ordering_by_age_ascending(self):
        response = self.client.get(self.list_url, {'ordering': 'age'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_results(response)
        ages = [s['age'] for s in results]
        self.assertEqual(ages, sorted(ages))
        self.assertEqual(ages[0], 21)
        self.assertEqual(ages[-1], 23)

    def test_ordering_by_age_descending(self):
        response = self.client.get(self.list_url, {'ordering': '-age'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_results(response)
        ages = [s['age'] for s in results]
        self.assertEqual(ages, sorted(ages, reverse=True))
        self.assertEqual(ages[0], 23)
        self.assertEqual(ages[-1], 21)

    def test_ordering_by_first_name_ascending(self):
        response = self.client.get(self.list_url, {'ordering': 'first_name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_results(response)
        names = [s['first_name'] for s in results]
        self.assertEqual(names, sorted(names))
        self.assertEqual(names[0], "Amit")

    def test_ordering_by_first_name_descending(self):
        response = self.client.get(self.list_url, {'ordering': '-first_name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_results(response)
        names = [s['first_name'] for s in results]
        self.assertEqual(names, sorted(names, reverse=True))
        self.assertEqual(names[0], "Rahul")

    def test_pagination_page_1(self):
        response = self.client.get(self.list_url, {'page': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 4)
        self.assertEqual(len(response.data['results']), 4)

    def test_pagination_custom_page_size(self):
        response = self.client.get(self.list_url, {'page': 1, 'page_size': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 4)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIsNotNone(response.data['next'])

    def test_pagination_page_2_with_page_size(self):
        response = self.client.get(self.list_url, {'page': 2, 'page_size': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 4)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIsNotNone(response.data['previous'])

    def test_pagination_invalid_page_returns_404(self):
        response = self.client.get(self.list_url, {'page': 999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class StudentValidationAPITests(APITestCase):

    def setUp(self):
        self.list_url = reverse('student-list')
        self.valid_payload = {
            "first_name": "Aakash",
            "last_name": "Mehta",
            "age": 20,
            "email": "aakash@example.com",
            "phone": "9876543210",
            "date_of_birth": "2004-06-15",
            "course": "B.Tech",
            "department": "CSE",
            "year": 2,
            "student_id": "STU2001",
            "address": "Chandigarh, India"
        }

    def get_errors(self, response):
        if isinstance(response.data, dict) and 'error' in response.data:
            return response.data['error'].get('details', response.data['error'])
        return response.data

    def test_negative_age_rejected(self):
        payload = {**self.valid_payload, "age": -5}
        response = self.client.post(self.list_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('age', self.get_errors(response))

    def test_excessive_age_rejected(self):
        payload = {**self.valid_payload, "age": 150}
        response = self.client.post(self.list_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('age', self.get_errors(response))

    def test_year_above_maximum_rejected(self):
        payload = {**self.valid_payload, "year": 10}
        response = self.client.post(self.list_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('year', self.get_errors(response))

    def test_year_zero_rejected(self):
        payload = {**self.valid_payload, "year": 0}
        response = self.client.post(self.list_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('year', self.get_errors(response))

    def test_invalid_email_format_rejected(self):
        payload = {**self.valid_payload, "email": "invalid-email-address"}
        response = self.client.post(self.list_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', self.get_errors(response))

    def test_invalid_phone_number_rejected(self):
        payload = {**self.valid_payload, "phone": "123"}
        response = self.client.post(self.list_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', self.get_errors(response))

    def test_future_date_of_birth_rejected(self):
        payload = {**self.valid_payload, "date_of_birth": "2099-01-01"}
        response = self.client.post(self.list_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('date_of_birth', self.get_errors(response))

    def test_valid_student_data_accepted(self):
        response = self.client.post(self.list_url, data=self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], "Aakash")
        self.assertEqual(response.data['age'], 20)


class StudentServiceUnitTests(APITestCase):

    def setUp(self):
        self.service = StudentService()
        self.student = self.service.create_student({
            "first_name": "Manoj",
            "last_name": "Tiwari",
            "age": 22,
            "email": "manoj@example.com",
            "phone": "9876543210",
            "date_of_birth": "2002-03-10",
            "course": "B.Tech",
            "department": "ECE",
            "year": 3,
            "student_id": "SVC001",
            "address": "Patna, India"
        })

    def test_service_get_student_by_id_exists(self):
        fetched = self.service.get_student_by_id(self.student.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.first_name, "Manoj")

    def test_service_get_student_by_id_not_found_returns_none(self):
        fetched = self.service.get_student_by_id(999999)
        self.assertIsNone(fetched)

    def test_service_create_student(self):
        new_student = self.service.create_student({
            "first_name": "Geeta",
            "last_name": "Rani",
            "age": 21,
            "email": "geeta@example.com",
            "phone": "9876543219",
            "date_of_birth": "2003-07-21",
            "course": "BCA",
            "department": "IT",
            "year": 2,
            "student_id": "SVC002",
            "address": "Kanpur, India"
        })
        self.assertEqual(new_student.first_name, "Geeta")
        self.assertTrue(Student.objects.filter(student_id="SVC002").exists())

    def test_service_update_student(self):
        updated = self.service.update_student(self.student, {"age": 23, "department": "EE"})
        self.assertEqual(updated.age, 23)
        self.assertEqual(updated.department, "EE")
        self.student.refresh_from_db()
        self.assertEqual(self.student.age, 23)

    def test_service_delete_student(self):
        result = self.service.delete_student(self.student)
        self.assertTrue(result)
        self.assertFalse(Student.objects.filter(id=self.student.id).exists())

    def test_service_list_students_filtering(self):
        results = self.service.list_students(department="ECE")
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().student_id, "SVC001")