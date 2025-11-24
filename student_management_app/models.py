from calendar import calendar
import re
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver 
from django.db.models.signals import post_save 
from django.apps import apps
from django.forms import DateTimeField



# Create your models here.

class SessionYearModel(models.Model):
    id=models.AutoField(primary_key=True)
    sessions_start_year=models.DateField()
    sessions_end_year=models.DateField()
    objects = models.Manager()
    def __str__(self):
        return f"{self.sessions_start_year} TO {self.sessions_end_year}"
class CustomUser(AbstractUser):
    user_type_data=((1,"HOD"),(2,"Staffs"),(3,"Students"))
    user_type=models.CharField(default=1,choices=user_type_data,max_length=10)

class AdminHOD(models.Model):
    id = models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class Staffs(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    fcm_token = models.TextField( null=True, blank=True)
    objects = models.Manager()

class Courses(models.Model):
    id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class Subjects(models.Model):
    id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=255)
    course_id = models.ForeignKey('courses', on_delete=models.CASCADE,default=1)
    staff_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
        
class Students(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10)
    profile_pic = models.FileField()
    address = models.TextField()
    course_id = models.ForeignKey('courses', on_delete=models.DO_NOTHING)
    session_year_id=models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    fcm_token = models.TextField( null=True, blank=True)
    objects = models.Manager()

class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    subject_id = models.ForeignKey('subjects', on_delete=models.DO_NOTHING) # type: ignore
    attendance_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    session_year_id=models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
         
class AttendanceReport(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey('students', on_delete=models.DO_NOTHING) # type: ignore
    attendance_id = models.ForeignKey('attendance', on_delete=models.CASCADE) # type: ignore
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class LeaveReportStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey('students', on_delete=models.CASCADE) # type: ignore
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    
class LeaveReportStaff(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey('staffs', on_delete=models.CASCADE) # type: ignore
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
               
class FeedbackStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey('students', on_delete=models.CASCADE) # type: ignore
    feedback = models.TextField(max_length=255)
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
                    
class FeedbackStaff(models.Model): 
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey('staffs', on_delete=models.CASCADE) # type: ignore
    feedback = models.TextField(max_length=255)
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
                        
class NotificationStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey('students', on_delete=models.CASCADE) # type: ignore
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
                            
class NotificationStaff(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey('staffs', on_delete=models.CASCADE) # type: ignore
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    
class StudentResult(models.Model):
    id=models.AutoField(primary_key=True)
    student_id=models.ForeignKey(Students,on_delete=models.CASCADE)
    subject_id=models.ForeignKey(Subjects,on_delete=models.CASCADE)
    subject_exam_marks=models.FloatField(default=0)
    subject_assignment_marks=models.FloatField(default=0)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now_add=True)
    objects=models.Manager()

class OnlineClassRoom(models.Model):
    id=models.AutoField(primary_key=True)
    room_name=models.CharField(max_length=255)
    room_pwd=models.CharField(max_length=255)
    subject=models.ForeignKey(Subjects,on_delete=models.CASCADE)
    session_years=models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    started_by=models.ForeignKey(Staffs,on_delete=models.CASCADE)
    is_active=models.BooleanField(default=True)
    created_on=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()   

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
            AdminHOD = apps.get_model('student_management_app', 'AdminHOD')
            Staffs = apps.get_model('student_management_app', 'Staffs')
            Students = apps.get_model('student_management_app', 'Students')
            if created:
                if instance.user_type==1:
                    AdminHOD.objects.create(admin=instance)
                if instance.user_type==2:
                    Staffs.objects.create(admin=instance, address="")
                if instance.user_type==3:
                    Students.objects.create(admin=instance,course_id=Courses.objects.get(id=1), session_year_id=SessionYearModel.objects.get(id=1), address="", gender="", profile_pic="")
                 
@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
            if instance.user_type==1:
                instance.adminhod.save()
                if instance.user_type==2:
                    instance.staffs.save()
                    if instance.user_type==3:
                        instance.students.save()