from django.urls import path
from .views import student_list, student_detail


urlpatterns = [
    path('students/', student_list, name='student-list'),
    path('students/<int:id>/', student_detail, name='student-detail'),
]