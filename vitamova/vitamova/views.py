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
import re

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
        #Make a list of tags for each paragraph named p1, p2, p3, etc.
        paragraphs = []
        s_index = 1
        w_index = 1
        #Create a word to sentence index
        w2s_map = []
        for i in range(len(article["text"])):
            #I want to add a span tag with ids s1, s2, s3, etc. for each sentence
            #I want to add a span tag with ids w1, w2, w3, etc. for each word
            #Sentences are separated by periods, question marks, and exclamation points
            sentences = re.split(r'\.|\?|\!',article["text"][i])
            for j in range(len(sentences)):
                words = sentences[j].split(" ")
                for k in range(len(words)):
                    w2s_map.append({"word":"w"+str(w_index),"sentence":"s"+str(s_index)})
                    words[k] = "<span id='w"+str(w_index)+"'>"+words[k]+"</span>"
                    w_index += 1
                sentences[j] = " ".join(words)
                sentences[j] = "<span id='s"+str(s_index)+"'>"+sentences[j]+"</span>"
                s_index += 1
            article["text"][i] = " ".join(sentences)
            paragraphs.append({"tag":"p"+str(i+1),"text":article["text"][i]})
        #Return the article title and the text as a list of paragraphs
        return render(request,'daily_article.html',{"title":article["title"],"paragraphs":paragraphs,"header":logged_in_header(),"w2s_map":w2s_map})
    else:
        return HttpResponseRedirect("/login/")
    
def poetry(request):
    #Check if user is logged in
    if request.user.is_authenticated:
        return render(request,'poetry.html',{"header":logged_in_header()})
    else:
        return HttpResponseRedirect("/login/")