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
import boto3

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
    
def daily_article(request):
    #Check if user is logged in
    if request.user.is_authenticated:
        #The filename we need is the current date in the format YYYY-MM-DD.json
        filename = str(datetime.date.today())+".json"
        #Create S3 Session
        #The AWS access key is an environment variable called AWS_ACCESS
        #The AWS secret key is an environment variable called AWS_SECRET
        #The AWS region is an environment variable called AWS_REGION
        aws_access_key_id = os.environ['AWS_ACCESS']
        aws_secret_access_key = os.environ['AWS_SECRET']
        aws_region = os.environ['AWS_REGION']
        my_session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        #Download the article from the bucket called evenstarsec.vitamova
        s3 = my_session.resource('s3')
        #The article is in the folder articles/spanish
        #The filename is the current date in the format YYYY-MM-DD.json
        obj = s3.Object('evenstarsec.vitamova', 'articles/spanish/'+filename)
        article = eval(obj.get()['Body'].read())
        #Return the article title and the text as a list of paragraphs
        return render(request,'daily_article.html',{"title":article["title"],"text":article["text"],"header":logged_in_header()})
    else:
        return HttpResponseRedirect("/login/")
    
def poetry(request):
    #Check if user is logged in
    if request.user.is_authenticated:
        return render(request,'poetry.html',{"header":logged_in_header()})
    else:
        return HttpResponseRedirect("/login/")