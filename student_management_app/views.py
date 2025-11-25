import json
from math import e
from pyexpat.errors import messages
import re
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout,authenticate
import requests
from student_management_app.emailbackend import EmailBackend
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from student_management_app.models import Courses, CustomUser, SessionYearModel, Staffs, Students
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage

# Create your views here.
def ShowDemoPage(request):
    return render(request, 'demo.html')

def ShowLoginPage(request):
    return render(request, 'login_page.html')

def dologin(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method not allowed</h2>")
    else:
        captcha_token=request.POST.get("g-recaptcha-response")
        cap_url="https://www.google.com/recaptcha/api/siteverify"
        cap_secret="6LfdDhQsAAAAABPu6J61pEkwz6GpqKlo-whJVbpi"
        cap_data={"secret":cap_secret,"response":captcha_token}
        cap_server_response=requests.post(url=cap_url,data=cap_data)
        cap_json=json.loads(cap_server_response.text)

        if cap_json['success']==False:
            messages.error(request,"Invalid Captcha Try Again")
            return HttpResponseRedirect("/")

        
        user = EmailBackend.authenticate(request,username=request.POST.get("email"), password=request.POST.get("password"))
        if user != None:
            login(request,user)
            if user.user_type == "1":
                return HttpResponseRedirect("/admin_home")
            elif user.user_type == "2":
                return HttpResponseRedirect(reverse("staff_home"))
            elif user.user_type == "3":
                return HttpResponseRedirect(reverse("student_home"))
        else:
            messages.error(request, "Invalid Login Details")    
            return HttpResponseRedirect("/")

# @login_required
def GetUserDetails(request):
    if request.user!=None:
           return HttpResponse(f"User: {request.user.email} UserType: {str(request.user.user_type)}")
    
    else:
        return HttpResponse("Please log in first.")

def logout_user(request):
        logout(request)
        return HttpResponseRedirect("/")

from django.http import HttpResponse
from django.template.loader import render_to_string

def showFirebaseJS(request):
    js = render_to_string('firebase-messaging-sw.js')
    return HttpResponse(js, content_type="application/javascript")

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def Testurl(request):
    _ = request.method
    return HttpResponse("Ok")

def signup_admin(request):
    return render(request,"signup_admin_page.html")

def signup_student(request):
    courses=Courses.objects.all()
    session_years=SessionYearModel.objects.all()
    return render(request,"signup_student_page.html",{"courses":courses,"session_years":session_years})

def signup_staff(request):
    return render(request,"signup_staff_page.html")

def do_admin_signup(request):
    username = request.POST.get("username")
    email = request.POST.get("email")
    password = request.POST.get("password")

    try:
        user=CustomUser.objects.create_user(username=username,password=password,email=email,user_type=1)
        user.save()
        messages.success(request,"Successfully Created Admin")
        return HttpResponseRedirect(reverse("show_login"))
    except:
        messages.error(request,"Failed to Create Admin")
        return HttpResponseRedirect(reverse("show_login"))

def do_staff_signup(request):
    username = request.POST.get("username")
    email = request.POST.get("email")
    password = request.POST.get("password")
    address = request.POST.get("address")

    try:
        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            email=email,
            user_type=2
        )

        Staffs.objects.create(
            admin=user,
            address=address
        )

        messages.success(request, "Successfully Created Staff")
        return HttpResponseRedirect(reverse("show_login"))

    except Exception as e:
        messages.error(request, f"Failed to Create Staff: {e}")
        return HttpResponseRedirect(reverse("show_login"))

def do_signup_student(request):
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    username = request.POST.get("username")
    email = request.POST.get("email")
    password = request.POST.get("password")
    address = request.POST.get("address")
    session_year_id = request.POST.get("session_year")
    course_id = request.POST.get("course")
    sex = request.POST.get("sex")

    profile_pic = request.FILES['profile_pic']
    fs = FileSystemStorage()
    filename = fs.save(profile_pic.name, profile_pic)
    profile_pic_url = fs.url(filename)

    try:
        # Create User
        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_type=3
        )

        # Fetch FK objects
        course_obj = Courses.objects.get(id=course_id)
        session_year_obj = SessionYearModel.objects.get(id=session_year_id)

        # Create Student object
        Students.objects.create(
            admin=user,
            gender=sex,
            profile_pic=profile_pic_url,
            address=address,
            course_id=course_obj,
            session_year_id=session_year_obj
        )

        messages.success(request, "Successfully Added Student")
        return HttpResponseRedirect(reverse("show_login"))

    except Exception as e:
        messages.error(request, f"Failed to Add Student: {e}")
        return HttpResponseRedirect(reverse("show_login"))