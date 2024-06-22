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

def home(request):
    return HttpResponseRedirect("/login/")