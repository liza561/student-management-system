
from fileinput import filename
import re
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from turtle import st
from django.forms import DateField
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from student_management_app.models import Courses, CustomUser, Staffs, Students,Attendance,AttendanceReport, Subjects,NotificationStudent,NotificationStaff,LeaveReportStudent ,SessionYearModel,LeaveReportStaff,FeedbackStaff,FeedbackStudent
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from student_management_app.forms import AddStudentForm, EditStudentForm 
from django.urls import reverse
from django.http import JsonResponse 
import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

def admin_home(request):
    student_count1=Students.objects.all().count()
    staff_count=Staffs.objects.all().count()
    subject_count=Subjects.objects.all().count()
    course_count=Courses.objects.all().count()

    course_all=Courses.objects.all()
    course_name_list=[]
    subject_count_list=[]
    student_count_list_in_course=[]
    for course in course_all:
        subjects=Subjects.objects.filter(course_id=course.id).count()
        students=Students.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)

    subjects_all=Subjects.objects.all()
    subject_list=[]
    student_count_list_in_subject=[]
    for subject in subjects_all:
        course=Courses.objects.get(id=subject.course_id.id)
        student_count=Students.objects.filter(course_id=course.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)

    staffs=Staffs.objects.all()
    attendance_present_list_staff=[]
    attendance_absent_list_staff=[]
    staff_name_list=[]
    for staff in staffs:
        subject_ids=Subjects.objects.filter(staff_id=staff.admin.id)
        attendance=Attendance.objects.filter(subject_id__in=subject_ids).count()
        leaves=LeaveReportStaff.objects.filter(staff_id=staff.id,leave_status=1).count()
        attendance_present_list_staff.append(attendance)
        attendance_absent_list_staff.append(leaves)
        staff_name_list.append(staff.admin.username)

    students_all=Students.objects.all()
    attendance_present_list_student=[]
    attendance_absent_list_student=[]
    student_name_list=[]
    for student in students_all:
        attendance=AttendanceReport.objects.filter(student_id=student.id,status=True).count()
        absent=AttendanceReport.objects.filter(student_id=student.id,status=False).count()
        leaves=LeaveReportStudent.objects.filter(student_id=student.id,leave_status=1).count()
        attendance_present_list_student.append(attendance)
        attendance_absent_list_student.append(leaves+absent)
        student_name_list.append(student.admin.username)


    return render(request,"Hod_templates/home_content.html",{"student_count":student_count1,"staff_count":staff_count,"subject_count":subject_count,"course_count":course_count,"course_name_list":course_name_list,"subject_count_list":subject_count_list,"student_count_list_in_course":student_count_list_in_course,"student_count_list_in_subject":student_count_list_in_subject,"subject_list":subject_list,"staff_name_list":staff_name_list,"attendance_present_list_staff":attendance_present_list_staff,"attendance_absent_list_staff":attendance_absent_list_staff,"student_name_list":student_name_list,"attendance_present_list_student":attendance_present_list_student,"attendance_absent_list_student":attendance_absent_list_student})

def add_staff(request):
    return render(request, 'hod_templates/add_staff_template.html')

def add_staff_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        address = request.POST.get("address")
        try:
            user=CustomUser.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name, user_type=2)
            user.save()
            staff_model=Staffs.objects.get(admin=user)
            staff_model.address=address
            staff_model.save()

            messages.success(request, "Successfully Added Staff")
            return HttpResponseRedirect(reverse("add_staff"))
        except Exception as e:
            messages.error(request, str(e))
            return HttpResponseRedirect(reverse("add_staff"))
        
def add_course(request):
    return render(request, 'hod_templates/add_course_template.html')    

def add_course_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        course=request.POST.get("course")
        try:
            course_model=Courses(course_name=course)
            course_model.save()
            messages.success(request, "Successfully Added Course")
            return HttpResponseRedirect(reverse("add_course"))
        except:
            messages.error(request, "Failed to Add Course")
            return HttpResponseRedirect(reverse("add_course"))
        
def add_student(request):
    form=AddStudentForm()
    courses = Courses.objects.all()
    return render(request,'hod_templates/add_student_template.html',{"form":form,"courses":courses})

def add_student_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        form=AddStudentForm(request.POST,request.FILES)
        if form.is_valid():
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            address = request.POST.get("address")
            session_year_id = request.POST.get("session_year_id")
            course_id = request.POST.get("course")
            sex = request.POST.get("sex")
            profile_pic = request.FILES.get("profile_pic", None)  # ✅ safe access
            profile_pic_url = ""

            if profile_pic:
                profile_pic = request.FILES.get('profile_pic', None)
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url=None   

            try:
                user=CustomUser.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name, user_type=3)
                user.save()
                student=Students.objects.get(admin_id=user.id)
                
                student.address=address
                course_objects=Courses.objects.get(id=course_id)
                student.course_id= course_objects
                session_year=SessionYearModel.objects.get(id=session_year_id)
                student.session_year_id=session_year
                student.gender=sex
                student.profile_pic=profile_pic_url
                student.save()

                messages.success(request, "Successfully Added Student")
                return HttpResponseRedirect(reverse("add_student"))
            except Exception as e:
                messages.error(request, str(e))
                return HttpResponseRedirect(reverse("add_student"))
        else:
            form=AddStudentForm(request.POST)
            return render(request,'hod_templates/add_student_template.html',{"form":form})
def add_subject(request):
    courses = Courses.objects.all()
    staffs=CustomUser.objects.filter(user_type=2)
    return render(request, 'hod_templates/add_Subject_template.html',{"courses":courses,"staffs":staffs})

def add_subject_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        subject_name=request.POST.get("subject_name")
        course_id=request.POST.get("course")
        course=Courses.objects.get(id=course_id)
        staff_id=request.POST.get("staff")
        staff=CustomUser.objects.get(id=staff_id)
        try:
            subject=Subjects(subject_name=subject_name, course_id=course, staff_id=staff)
            subject.save()
            
            messages.success(request, "Successfully Added Subject")
            return HttpResponseRedirect(reverse("add_subject"))
        except:
            messages.error(request, "Failed to Add Subject")
            return HttpResponseRedirect(reverse("add_subject"))
        
def manage_staff(request):
    staffs=Staffs.objects.all()
    return render(request, 'hod_templates/manage_staff_template.html',{"staffs":staffs})  

def manage_student(request):
    students=Students.objects.all()
    return render(request, 'hod_templates/manage_student_template.html',{"students":students})

def manage_course(request):
    courses=Courses.objects.all()
    return render(request, 'hod_templates/manage_course_template.html',{"courses":courses})

def manage_subject(request):
    subjects=Subjects.objects.all()
    return render(request, 'hod_templates/manage_subject_template.html',{"subjects":subjects})

def edit_staff(request, staff_id):
    staff=Staffs.objects.get(admin=staff_id)
    return render(request, 'hod_templates/edit_staff_template.html',{"staff":staff , "id":staff_id})
    
def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        staff_id = request.POST.get("staff_id")
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        address = request.POST.get("address")
        
        try:
            user=CustomUser.objects.get(id=staff_id)
            user.email=email
            user.first_name=first_name      
            user.last_name=last_name
            user.username=username
            user.save()
        
            staff_model=Staffs.objects.get(admin=staff_id)
            staff_model.address=address
            staff_model.save()
            messages.success(request, "Successfully Updated Staff")
            return HttpResponseRedirect(reverse("edit_staff" ,kwargs={"staff_id":staff_id}))
        except:
            messages.error(request, "Failed to Update Staff")
            return HttpResponseRedirect(reverse("edit_staff" ,kwargs={"staff_id":staff_id}))
        
def edit_student(request, student_id):
    request.session['student_id'] = student_id
    student=Students.objects.get(admin=student_id)
    form=EditStudentForm()
    form.fields['email'].initial=student.admin.email
    form.fields['first_name'].initial=student.admin.first_name
    form.fields['last_name'].initial=student.admin.last_name
    form.fields['username'].initial=student.admin.username
    form.fields['address'].initial=student.address
    form.fields['course'].initial=student.course_id.id
    form.fields['sex'].initial=student.gender
    form.fields['session_year_id'].initial=student.session_year_id.id
    return render(request, 'hod_templates/edit_student_template.html',{"form":form,"id":student_id,"username":student.admin.username})       

def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        student_id = request.session.get("student_id")
        if student_id==None:
         return HttpResponseRedirect("/manage_student") 
        
        form=EditStudentForm(request.POST,request.FILES)
        if form.is_valid():
            email = form.cleaned_data["email"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            address = form.cleaned_data["address"]
            course_id = form.cleaned_data["course"]
            session_year_id = form.cleaned_data["session_year_id"]
            sex = form.cleaned_data["sex"]
            
            profile_pic = request.FILES.get('profile_pic', None)
            if profile_pic:
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url=None 
            
            try:                
                user=CustomUser.objects.get(id=student_id)
                user.email=email
                user.first_name=first_name      
                user.last_name=last_name
                user.username=username
                user.save()
            
                student=Students.objects.get(admin_id=student_id)
                student.address= address
                course=Courses.objects.get(id=course_id)
                student.course_id=course
                session_year=SessionYearModel.objects.get(id=session_year_id)
                student.session_year_id=session_year
                student.gender= sex
                if profile_pic_url!=None:
                    student.profile_pic=profile_pic_url
                student.save()
                del request.session['student_id']
                messages.success(request, "Successfully Updated Student")
                return HttpResponseRedirect(reverse("edit_student" , kwargs={"student_id":student_id}))
            
            except :
                messages.error(request, "Failed to Update Student")
                return HttpResponseRedirect(reverse("edit_student" ,kwargs={"student_id":student_id}))
        else:
            form=EditStudentForm(request.POST)  
            student=Students.objects.get(admin=student_id)
            return render(request, 'hod_templates/edit_student_template.html',{"form":form,"id":student_id,"username":student.admin.username})




def edit_subject(request,subject_id):
    subject = Subjects.objects.get(id=subject_id)
    course = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type=2)
    return render(request,"hod_templates/edit_subject_template.html",{"subject":subject,"staffs":staffs,"courses":course, "id":subject_id})

def edit_subject_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    
    else:
        subject_id = request.POST.get("subject_id")
        subject_name = request.POST.get("subject_name")
        staff_id = request.POST.get("staff")
        course_id = request.POST.get("course")
        try:
            subject = Subjects.objects.get(id=subject_id)
            subject.subject_name = subject_name
            staff=CustomUser.objects.get(id=staff_id)
            subject.staff_id=staff
            course=Courses.objects.get(id=course_id)
            subject.course_id=course
            subject.save()
            messages.success(request, "Successfully Updated Subject")
            return HttpResponseRedirect(reverse("edit_subject",kwargs={"subject_id":subject_id}))
        except:
            messages.error(request, "Failed to Update Subject")
            return HttpResponseRedirect(reverse("edit_subject/", kwargs={"subject_id":subject_id}))     

def edit_course(request, course_id):
    course=Courses.objects.get(id=course_id)
    return render(request,"hod_templates/edit_course_template.html",{"course":course, "id":course_id})
    

def edit_course_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    
    else:
        course_id = request.POST.get("course_id")
        course_name = request.POST.get("course")
        
        try:
            course = Courses.objects.get(id=course_id)
            course.course_name = course_name
            course.save()
            messages.success(request, "Successfully Updated Course")
            return HttpResponseRedirect(reverse("edit_course", kwargs={"course_id":course_id}))
        except:
            messages.error(request, "Failed to Update Course")
            return HttpResponseRedirect(reverse("edit_course",kwargs={"course_id":course_id}))
        
def manage_session(request):
    return render(request,"hod_templates/manage_session_template.html")

def add_session_save(request):
     if request.method != "POST":
        return HttpResponseRedirect(reverse("manage_session"))
    
     else:
        sessions_start_year=request.POST.get("session_start")
        sessions_end_year=request.POST.get("session_end")   
        
        try:    
            sessionyear=SessionYearModel(sessions_start_year=sessions_start_year,sessions_end_year=sessions_end_year)   
            sessionyear.save()
            messages.success(request, "Successfully Added Session")
            return HttpResponseRedirect(reverse("manage_session"))
        except Exception as e:
            messages.error(request, str(e))
            return HttpResponseRedirect(reverse("manage_session"))
        
@csrf_exempt
def check_email_exist(request):
    email=request.POST.get("email")
    print("Received Email:", email)
    user_obj=CustomUser.objects.filter(email=email).exists()
    print("Exists:", user_obj)
    if user_obj:
        return HttpResponse("True")
    else:
        return HttpResponse("False")

@csrf_exempt
def check_username_exist(request):
    username=request.POST.get("username")
    user_obj=CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse("True")
    else:
        return HttpResponse("False")
            
            
def staff_feedback_message(request):
    feedbacks=FeedbackStaff.objects.all()
    return render(request,"Hod_templates/staff_feedback_template.html",{"feedbacks":feedbacks})


def student_feedback_message(request):
    feedbacks=FeedbackStudent.objects.all()
    return render(request,"Hod_templates/student_feedback_template.html",{"feedbacks":feedbacks})

@csrf_exempt
def student_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedbackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

@csrf_exempt
def staff_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedbackStaff.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")
    
def staff_leave_view(request):
    leaves=LeaveReportStaff.objects.all()
    return render(request,"Hod_templates/staff_leave_view.html",{"leaves":leaves})

def student_leave_view(request):
    leaves=LeaveReportStudent.objects.all()
    return render(request,"Hod_templates/student_leave_view.html",{"leaves":leaves})

def student_approve_leave(request,leave_id):
    leave=LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))

def student_disapprove_leave(request,leave_id):
    leave=LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))


def staff_approve_leave(request,leave_id):
    leave=LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))

def staff_disapprove_leave(request,leave_id):
    leave=LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))

def admin_view_attendance(request):
    subjects=Subjects.objects.all()
    session_year_id=SessionYearModel.objects.all()
    return render(request,"Hod_templates/admin_view_attendance.html",{"subjects":subjects,"session_year_id":session_year_id})

@csrf_exempt
def admin_get_attendance_date(request):
    subject_id=request.POST.get("subject")
    session_year_id=request.POST.get("session_year_id")
    subject_obj=Subjects.objects.get(id=subject_id)
    session_year_obj=SessionYearModel.objects.get(id=session_year_id)
    attendance=Attendance.objects.filter(subject_id=subject_obj,session_year_id=session_year_obj)
    attendance_obj=[]
    for attendance_single in attendance:
        data={"id":attendance_single.id,"attendance_date":str(attendance_single.attendance_date),"session_year_id":attendance_single.session_year_id.id}
        attendance_obj.append(data)

    return JsonResponse(attendance_obj,safe=False)


@csrf_exempt
def admin_get_attendance_student(request):
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)

    attendance_data=AttendanceReport.objects.filter(attendance_id=attendance)
    list_data=[]

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id,"name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name,"status":student.status}
        list_data.append(data_small)
    return JsonResponse(list_data,content_type="application/json",safe=False)

def admin_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    return render(request,"Hod_templates/admin_profile.html",{"user":user})

def admin_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("admin_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        password=request.POST.get("password")
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name
            # if password!=None and password!="":
            #     customuser.set_password(password)
            customuser.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("admin_profile"))
        except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("admin_profile"))

def admin_send_notification_student(request):
    students=Students.objects.all()
    return render(request,"Hod_templates/student_notification.html",{"students":students})

def admin_send_notification_staff(request):
    staffs=Staffs.objects.all()
    return render(request,"Hod_templates/staff_notification.html",{"staffs":staffs})

import time

_access_token_cache = {
    "token": None,
    "expiry": 0
}

def get_access_token():
    SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]
    SERVICE_ACCOUNT_FILE = "serviceAccountKey.json"

    now = time.time()
    # If token is valid, return cached token
    if _access_token_cache["token"] and _access_token_cache["expiry"] > now + 60:
        return _access_token_cache["token"]

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    request = google.auth.transport.requests.Request()
    credentials.refresh(request)

    _access_token_cache["token"] = credentials.token
    _access_token_cache["expiry"] = credentials.expiry.timestamp() if credentials.expiry else now + 3500

    return credentials.token


@csrf_exempt
def send_student_notification(request):
    id = request.POST.get("id")
    message = request.POST.get("message")

    try:
        student = Students.objects.get(admin=id)
        token = student.fcm_token

        if token is None or token == "":
            return HttpResponse("False")   # No FCM token

        url = "https://fcm.googleapis.com/v1/projects/student-1067a/messages:send"

        access_token= get_access_token()
        print(access_token)
        headers = {
        "Content-Type": "application/json",
        "Authorization": "15ba1cb44249f19281786cc3c1230cd791a9f0d5" + settings.FCM_SERVER_KEY
        }

        body = {
            "message": {
                "token": token,
                "notification": {
                    "title": "Student Management System",
                    "body": message
                },
                "data": {
                    "click_action": "FLUTTER_NOTIFICATION_CLICK"
                }
            }
        }

        response = requests.post(url, headers=headers, json=body)
        print("FCM STATUS:", response.status_code)
        print("FCM RESPONSE:", response.text)


        if response.status_code == 200:
            # Save notification in DB
            notification_obj = NotificationStudent(student_id=student, message=message)
            notification_obj.save()

            return HttpResponse("True")

        else:
            print(response.text)
            return HttpResponse("False")

    except Exception as e:
        print("Error:", e)
        return HttpResponse("False")


@csrf_exempt
def send_staff_notification(request):
    try:
        data = request.POST
        staff_id = data.get("id")  # optional: if None, send to all
        message = data.get("message")

        if not message:
            return HttpResponse("False")

        # Determine recipients
        if staff_id:
            staff_list = [Staffs.objects.get(admin=staff_id)]
        else:
            staff_list = Staffs.objects.exclude(fcm_token__isnull=True).exclude(fcm_token__exact="")

        access_token = get_access_token()
        url = "https://fcm.googleapis.com/v1/projects/student-1067a/messages:send"

        for staff in staff_list:
            token = staff.fcm_token
            if not token:
                print(f"No FCM token for {staff.admin.username}")
                continue

            body = {
                "message": {
                    "token": token,
                    "notification": {"title": "SMS", "body": message},
                    "webpush": {"fcm_options": {"link": "https://yourdomain.com/staff_all_notification"}}
                }
            }

            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}
            response = requests.post(url, headers=headers, data=json.dumps(body))
            print("FCM Response:", response.text)

            # Save in DB
            NotificationStaff.objects.create(staff_id=staff, message=message)

        return HttpResponse("True")

    except Exception as e:
        print("Error sending notification:", e)
        return HttpResponse("False")