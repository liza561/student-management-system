import json
from math import e
from pyexpat.errors import messages
import re
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout,authenticate
from student_management_app.emailbackend import EmailBackend
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from student_management_app.models import Courses, CustomUser, Staffs
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


# Create your views here.
def ShowDemoPage(request):
    return render(request, 'demo.html')

def ShowLoginPage(request):
    return render(request, 'login_page.html')

def dologin(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method not allowed</h2>")
    else:
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


@csrf_exempt
def staff_save_fcm_token(request):
    if request.method == "POST":
        data = json.loads(request.body)
        token = data.get("token")
        try:
            staff = Staffs.objects.get(admin=request.user.id)
            staff.fcm_token = token
            staff.save()
            return JsonResponse({"status": "success"})
        except Staffs.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Staff not found"}, status=404)
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)