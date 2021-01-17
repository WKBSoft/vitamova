# coding=utf-8
from random import shuffle
from random import randint
import boto3
import os
import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import sys
import re
import urllib
import boto3
import json
import hashlib
import secrets

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR,'scripts/'))
import ukrainian
import content_gen
import ua_alphabet
#translate_key = urllib.parse.unquote(request.GET.get('translate',""))

def logged_in_header():
    with open(os.path.join(BASE_DIR,"templates/sub_templates/logged_in_header.html"),"r") as f:
        return f.read()

def check_login(request):
    #Returns 3 results 0=correct login, 1=incorrect login, 2=no account
    login_email = request.POST["email"]
    login_token = request.POST["login_token"]
    if login_email != "" and login_token != "":
        with open("/home/ubuntu/users/userpass.json","r") as f:
            userpass = json.load(f)
    else:
        return 1
    if login_email in userpass:
        user_info = userpass[login_email]
    else:
        return 2
    if user_info["token"] == login_token:
        return 0
    else:
        return 1
        
def home(request):
    return HttpResponseRedirect("/dashboard")

def login(request):
    secret_token = secrets.token_urlsafe(64)
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        login_token = request.POST["login_token"]
        with open("/home/ubuntu/users/userpass.json","r") as f:
            userpass = json.load(f)
        pass_b = bytes(password,encoding="utf-8")
        pash_hash = hashlib.sha256(pass_b).hexdigest()
        if userpass[email]["password"] == pash_hash:
            userpass[email]["token"] = login_token
            with open("/home/ubuntu/users/userpass.json","w+") as f:
                json.dump(userpass,f)
            return HttpResponseRedirect('/dashboard')
        else:
            return(render(request,'login.html',{"randomvalue":secret_token}))
    else:
        return(render(request,'login.html',{"randomvalue":secret_token}))

def logout(request):
    return render(request,'logout.html',{}) 

def signup(request):
    if request.method == "GET":
        return render(request,'signup.html',{})
    else:
        login_email = request.POST["email"]
        password = request.POST["password"]
        pass_b = bytes(password,encoding="utf-8")
        pass_hash = hashlib.sha256(pass_b).hexdigest()
        with open("/home/ubuntu/users/userpass.json","r") as f:
            userpass = json.load(f)
        if login_email not in userpass:
            userpass.update({login_email:{"password":pass_hash,"token":""}})
            with open("/home/ubuntu/users/userpass.json","w+") as f:
                json.dump(userpass,f)
            user_data = {"transcribe": {"level": "0"}, "read": {"level": "0"}, "start_date":str(datetime.date.today()),"history":[0]}
            with open("/home/ubuntu/users/userdata/"+login_email+".json","w+") as f:
                json.dump(user_data,f)
            return HttpResponseRedirect('/login')
        else:
            return render(request,'signup.html',{})
        

def dashboard(request):
    if request.method == "GET":
        return render(request,'authenticator.html',{"url":"/dashboard/"})
    else:
        login_email = request.POST["email"]
        login_token = request.POST["login_token"]
        if login_email != "" and login_token != "":
            with open("/home/ubuntu/users/userpass.json","r") as f:
                userpass = json.load(f)
            user_info = userpass[login_email]
            if user_info["token"] == login_token:
                with open("/home/ubuntu/users/userdata/"+login_email+".json","r") as f:
                    user_data = json.load(f)
                history = user_data["history"]
                start_date = user_data["start_date"].split("-")
                date_delta = (datetime.date.today() - datetime.date(int(start_date[0]),int(start_date[1]),int(start_date[2]))).days
                if len(history) < date_delta+1:
                    history += [0] * (date_delta+1-len(history))
                    with open("/home/ubuntu/users/userdata/"+login_email+".json","w+") as f:
                        json.dump(user_data,f)
                if len(history) < 7:
                    week_score = "0"
                else:
                    week_points = sum(history[len(history)-7:len(history)])/7
                    better_than = len(list(filter(lambda x: x<week_points,history)))
                    week_score = str((100.0*better_than)//len(history))
                if len(history) < 30:
                    month_score = "0"
                else:
                    month_points = sum(history[len(history)-30:len(history)])/30
                    better_than = len(list(filter(lambda x: x<month_points,history)))
                    month_score = str((100.0*better_than)//len(history))
                day_points = history[len(history)-1]
                better_than = len(list(filter(lambda x: x<day_points,history)))
                day_score = str((100.0*better_than)//len(history))
                data = {"day_score":day_score,"week_score":week_score,"month_score":month_score,"header":logged_in_header()}
                return(render(request,'dashboard.html',data))
            else:
                return HttpResponseRedirect('/login')
        else:
            return HttpResponseRedirect('/login')

def read(request):
    if request.method == "GET":
        return render(request,'authenticator.html',{"url":"/read/"})
    else:
        login_email = request.POST["email"]
        login_token = request.POST["login_token"]
        with open("/home/ubuntu/users/userpass.json","r") as f:
            userpass = json.load(f)
        user_info = userpass[login_email]
        if user_info["token"] == login_token:
            with open("/home/ubuntu/users/userdata/"+login_email+".json","r") as f:
                user_data = json.load(f)
            if "read" not in user_data:
                user_data.update({"read":{"level":"0"}})
                with open("/home/ubuntu/users/userdata/"+login_email+".json","w+") as f:
                    json.dump(user_data,f)
            read_level = int(user_data["read"]["level"])
            with open("/home/ubuntu/vitamova/content/read_text_"+str(read_level)+".txt","r") as f:
                read_content = f.read()
            read_content_l = str(len(re.split(r'[\s-]',read_content)))
            read_content = "<p>" + read_content + "</p>"
            read_content = read_content.replace("\n","</p><p>")
            return(render(request,"read.html",{ "read_text":read_content, "word_count":read_content_l}))
        else:
            return HttpResponseRedirect('/login')
    
def transcription_submit(request):
    return HttpResponseRedirect('/transcribe')

def flashcards(request):
    return render(request,'coming_soon.html',{})

def reader(request):
    book_title = request.GET['title']
    if not os.path.isfile('/home/ubuntu/books/'+book_title):
        s3 = boto3.resource('s3')
        s3.Object('wkbvitamova', 'books/'+book_title).download_file('/home/ubuntu/books/'+book_title)
    default_page = "0"
    return(render(request,'reader.html',{'book_title':book_title,'default_page':default_page}))

def get_book(request):
    book_title = urllib.parse.unquote(request.GET['title'])
    book_page = request.GET['page']
    with open('/home/ubuntu/books/'+book_title,'r') as f:
        file_data = f.read()
    book_pages = urllib.parse.quote(ukrainian.return_pages(file_data,200,book_page))
    return HttpResponse(book_pages, content_type="text/plain")

def translate(request):
    translate_key = request.GET.get('word_key',"")
    translation = ukrainian.translate(urllib.parse.quote(translate_key))
    #translation = urllib.parse.quote(translation)
    return HttpResponse(translation, content_type="text/plain")

def transcribe(request):
    if request.method == "GET":
        return render(request,'authenticator.html',{"url":"/transcribe/"})
    else:
        login_email = request.POST["email"]
        login_token = request.POST["login_token"]
        with open("/home/ubuntu/users/userpass.json","r") as f:
            userpass = json.load(f)
        user_info = userpass[login_email]
        if user_info["token"] == login_token:
            with open("/home/ubuntu/users/userdata/"+login_email+".json","r") as f:
                user_data = json.load(f)
            if "transcribe" not in user_data:
                user_data.update({"transcribe":{"level":"0"}})
                with open("/home/ubuntu/users/userdata/"+login_email+".json","w+") as f:
                    json.dump(user_data,f)
            transcribe_level = int(user_data["transcribe"]["level"])
            with open("/home/ubuntu/vitamova/content/transcribe_embed.txt","r") as f:
                transcribe_srcs = f.readlines()
            transcribe_src = transcribe_srcs[transcribe_level]
            with open("/home/ubuntu/vitamova/content/transcribe_text_"+str(transcribe_level)+".txt","r") as f:
                transcription_content = f.read()
            transcription_content_l = transcription_content.split(" ")
            for i in range(len(transcription_content_l)):
                word_bytes = bytes(transcription_content_l[i],encoding="utf-8")
                transcription_content_l[i] = hashlib.sha256(word_bytes).hexdigest()
            transcription_content = " ".join(transcription_content_l)
            return(render(request,"transcribe.html",{"transcribe_src":transcribe_src, "video_content":transcription_content}))
        else:
            return HttpResponseRedirect('/login')

def accent(request):
    return render(request,"accent.html",{})
    
def write(request):
    return render(request,'coming_soon.html',{})
    
def typing(request):
    if request.method == "GET":
        return render(request,'authenticator.html',{"url":"/typing/"})
    elif request.method == "POST":
        if 'request' not in request.POST:
            logged_in = check_login(request)
            print(logged_in)
            if logged_in == 2:
                return HttpResponseRedirect("/signup")
            if logged_in == 1:
                return HttpResponseRedirect("/login")
            if logged_in == 0:
                return render(request,'typing.html',{"header":logged_in_header()})
        else:
            if request.POST['request'] == 'wlu':
                client = boto3.client('s3')
                articles_list_r = client.list_objects_v2(Bucket='wkbvitamova',Prefix='articles/')
                articles_list = articles_list_r['Contents']
                selector = randint(0,len(articles_list)-1)
                key = articles_list[selector]['Key']
                s3 = boto3.resource('s3')
                object = s3.Object('wkbvitamova',key)
                article_content = object.get()['Body'].read().decode("utf-8")
                response_l = ua_alphabet.split_word_list(article_content)
                shuffle(response_l)
                response = "|".join(response_l[0:20])
                return HttpResponse(response, content_type="text/plain")
        