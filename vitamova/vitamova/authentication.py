from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib import auth
import os
import sys
import hashlib
import datetime
import copy
from pathlib import Path
import json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

#sys.path.insert(0, os.path.join(BASE_DIR,'scripts/'))
#import database as db

def logged_in_header():
    with open(os.path.join(BASE_DIR,"templates/sub_templates/logged_in_header.html"),"r") as f:
        return f.read()

def not_logged_in_header():
    with open(os.path.join(BASE_DIR,"templates/sub_templates/not_logged_in_header.html"),"r") as f:
        return f.read()

class user_data_c:
    def __init__(self,email):
        self.email = email
    def get(self):
        return 0 #db.retrieve("userdata",self.email)
    def put(self,data):
        return 0 #db.send("userdata",self.email,data)
    def delete(self):
        return 0 #db.delete("userdata")

def userpass_get():
    return 0 #db.retrieve("userpass","1")
    
def userpass_put(data):
    return 0 #db.send("userpass","1",data)

def login(request):
    if request.method == "GET":
        return render(request,'login.html',{"header":not_logged_in_header()})
    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return render(request,'dashboard.html',{"header":logged_in_header()})
        else:
            return render(request,'login.html',{"header":not_logged_in_header()})

def signup(request):
    if request.method == "GET":
        return render(request,'signup.html',{"header":not_logged_in_header()})
    else:
        login_email = request.POST["email"]
        password = request.POST["password"]
        pass_b = bytes(password,encoding="utf-8")
        pass_hash = hashlib.sha256(pass_b).hexdigest()
        userpass = userpass_get()
        if login_email not in userpass:
            userpass.update({login_email:{"password":pass_hash}})
            userpass_put(userpass)
            user_data = {
                "transcribe": {"level": "0"},
                "read": {"articles": 0},
                "typing": {"level": "0"},
                "start_date":str(datetime.date.today()),
                "history":[0],"points":0
            }
            user_data_c(login_email).put(user_data)
            return HttpResponseRedirect('/login')
        else:
            return render(request,'signup.html',{"header":not_logged_in_header()})

def account(request):
    if request.method == "GET":
        return render(request,'authenticator.html',{"url":"/account/"})
    elif request.method == "POST":
        logged_in = check_login(request)
        if logged_in == 2:
            return HttpResponseRedirect("/signup")
        if logged_in == 1:
            return HttpResponseRedirect("/login")
        if logged_in == 0:
            if "request" not in request.POST:
                return render(request, 'account.html',{"header":logged_in_header()})
            else:
                email = request.POST["email"]
                if request.POST["request"] == "delete":
                    userpass = userpass_get()
                    del userpass[email]
                    userpass_put(userpass)
                    user_data_c(email).delete()
                    return HttpResponse("success", content_type="text/plain")
                if request.POST["request"] == "changeemail":
                    userpass = userpass_get()
                    new_email = request.POST["new_email"]
                    if new_email in userpass:
                        return HttpResponse("already_exists", content_type="text/plain")
                    userpass[new_email] = copy.copy(userpass[email])
                    userdata = user_data_c(email).get()
                    user_data_c(new_email).put(userdata)
                    user_data_c(email).delete()
                    del userpass[email]
                    userpass_put(userpass)
                    return HttpResponse("success", content_type="text/plain")
                if request.POST["request"] == "changepassword":
                    userpass = userpass_get()
                    new_password = request.POST["new_password"]
                    pass_b = bytes(new_password,encoding="utf-8")
                    pass_hash = hashlib.sha256(pass_b).hexdigest()
                    userpass[email]["password"] = pass_hash
                    userpass_put(userpass)
                    return HttpResponse("success", content_type="text/plain")
            
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/login/")

def update_account(request):
    #Check if user is logged in
    if request.user.is_authenticated:
        #Get the request json data
        data = json.loads(request.body)
        #Get the user object
        user = request.user
        u = auth.models.User.objects.get(username=user)
        if "email" in data:
            u.email = data["email"]
        if "first_name" in data:
            u.first_name = data["first_name"]
        if "last_name" in data:
            u.last_name = data["last_name"]
        return HttpResponse("success", content_type="text/plain")
    else:
        return HttpResponse(status=403)