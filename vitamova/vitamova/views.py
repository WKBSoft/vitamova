from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse 
from django.contrib import auth
import datetime
import os
import sys
import requests
from random import randint
import hashlib
from random import shuffle

def home(request):
    #Check if user is logged in
    if request.user.is_authenticated:
        return render(request,'dashboard.html',{"header":logged_in_header()})
    else:
        return HttpResponseRedirect("/login/")