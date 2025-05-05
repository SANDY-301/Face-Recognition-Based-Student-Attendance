from django.db import models
from datetime import datetime

class Student(models.Model):
    name = models.CharField(max_length=100)
    reg_no = models.CharField(max_length=50, primary_key=True)
    phone_no = models.CharField(max_length=15)
    class_name = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class StudentImage(models.Model):
    student = models.ForeignKey(Student, to_field='reg_no', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/student_images/')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.student.name} ({self.student.reg_no})"


class Attendance(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    reg_no = models.ForeignKey(Student, on_delete=models.CASCADE)

    SESSION_CHOICES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon')
    ]
    session = models.CharField(max_length=10, choices=SESSION_CHOICES)

    PERIOD_CHOICES = [
        ('1st_hour', '1st Hour'),
        ('2nd_hour', '2nd Hour'),
        ('3rd_hour', '3rd Hour'),
        ('4th_hour', '4th Hour'),
        ('5th_hour', '5th Hour')
    ]
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)

    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    date = models.DateField(default=datetime.today)

    def __str__(self):
        return f"{self.reg_no.name} - {self.session} - {self.period} - {self.status}"

from django.db import models
from datetime import datetime
from .models import Student  # Import the existing Student model

class AttendanceReport(models.Model):
    report_id = models.AutoField(primary_key=True)
    reg_no = models.ForeignKey(Student, on_delete=models.CASCADE)
    present_days = models.IntegerField(default=0)
    full_day_present = models.IntegerField(default=0)
    half_day_present = models.IntegerField(default=0)
    half_day_absent = models.IntegerField(default=0)
    full_day_absent = models.IntegerField(default=0)
    remaining_leave_days = models.IntegerField(default=27)  # Max leave days
    percentage = models.FloatField(default=0.0)
    date = models.DateField(default=datetime.today)

    def __str__(self):
        return f"Report for {self.reg_no.name} ({self.reg_no.reg_no}) - {self.date}"

    def student_name(self):
        return self.reg_no.name

    def student_class(self):
        return self.reg_no.class_name

    def student_phone(self):
        return self.reg_no.phone_no
