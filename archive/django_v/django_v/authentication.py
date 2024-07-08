from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
import os
import sys
import hashlib
import datetime
import copy

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.path.join(BASE_DIR,'scripts/'))
import database as db

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
        return db.retrieve("userdata",self.email)
    def put(self,data):
        return db.send("userdata",self.email,data)
    def delete(self):
        return db.delete("userdata")

def userpass_get():
    return db.retrieve("userpass","1")
    
def userpass_put(data):
    return db.send("userpass","1",data)

def check_login(request):
    #Returns 3 results 0=logged in, 1=not logged in, 2=no account
    login_email = request.POST["email"]
    login_token = request.POST["login_token"]
    if login_email != "" and login_token != "":
        userpass = userpass_get()
    else:
        return 1
    if login_email in userpass:
        user_info = userpass[login_email]
    else:
        return 2
    if "token" not in user_info:
        return 1
    if user_info["token"] == login_token:
        return 0
    else:
        return 1

def login(request):
    if request.method == "GET":
        return render(request,'authenticator.html',{"url":"/login/"})
    else:
        if "logging_in" not in request.POST:
            logged_in = check_login(request)
            if logged_in == 0:
                return HttpResponseRedirect('/dashboard')
            else:
                return(render(request,'login.html',{"header":not_logged_in_header()}))
        else:
               email = request.POST["email"]
               userpass = userpass_get()
               if email not in userpass:
                   return render(request,'login.html',{"header":not_logged_in_header()})
               else:
                   password = request.POST["password"]
                   login_token = request.POST["login_token"]
                   pass_b = bytes(password,encoding="utf-8")
                   pash_hash = hashlib.sha256(pass_b).hexdigest()
                   if userpass[email]["password"] == pash_hash:
                       userpass[email]["token"] = login_token
                       userpass_put(userpass)
                       return HttpResponseRedirect('/dashboard')
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
    return render(request,'logout.html',{}) 