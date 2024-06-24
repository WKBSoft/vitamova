from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse 
import datetime
import os
import sys
import requests
from random import randint
import hashlib
from random import shuffle
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

def logged_in_header():
    with open(os.path.join(BASE_DIR,"templates/sub_templates/logged_in_header.html"),"r") as f:
        return f.read()

def not_logged_in_header():
    with open(os.path.join(BASE_DIR,"templates/sub_templates/not_logged_in_header.html"),"r") as f:
        return f.read()

def home(request):
    #Check if user is logged in
    if request.user.is_authenticated:
        return render(request,'dashboard.html',{"header":logged_in_header()})
    else:
        return HttpResponseRedirect("/login/")