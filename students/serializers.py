import re
from datetime import date
from rest_framework import serializers
from .models import Student


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = '__all__'

    def validate_first_name(self, value):
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise serializers.ValidationError("First name must be at least 2 characters long.")
        return cleaned

    def validate_last_name(self, value):
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise serializers.ValidationError("Last name must be at least 2 characters long.")
        return cleaned

    def validate_age(self, value):
        if value < 15 or value > 100:
            raise serializers.ValidationError("Age must be between 15 and 100.")
        return value

    def validate_year(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Academic year must be between 1 and 5.")
        return value

    def validate_phone(self, value):
        cleaned = re.sub(r'[\s\-]', '', value)
        if not re.match(r'^\+?[0-9]{10,15}$', cleaned):
            raise serializers.ValidationError("Phone number must contain between 10 and 15 digits.")
        return cleaned

    def validate_email(self, value):
        cleaned = value.strip().lower()
        if not re.match(r'^[\w\.\-]+@[\w\-]+\.[a-zA-Z]{2,}$', cleaned):
            raise serializers.ValidationError("Enter a valid email address.")
        return cleaned

    def validate_date_of_birth(self, value):
        if value >= date.today():
            raise serializers.ValidationError("Date of birth must be in the past.")
        return value