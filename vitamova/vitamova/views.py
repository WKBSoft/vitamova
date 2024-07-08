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
from pathlib import Path
import boto3
import re
import json
from openai import OpenAI

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
        return render(request,'dashboard.html',{"header":logged_in_header(), "user":request.user, "date":str(datetime.datetime.now().date())})
    else:
        return HttpResponseRedirect("/login/")
    
def account(request):
    #Check if user is logged in
    if request.user.is_authenticated:
        return render(request,'account.html',{"header":logged_in_header(), "user":request.user})
    else:
        return HttpResponseRedirect("/login/")
    
def daily_article(request):
    #Check if user is logged in
    if request.user.is_authenticated:
        #The filename we need is the current date in the format YYYY-MM-DD.json
        filename = str(datetime.datetime.now().date())+".json"
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
        print(filename)
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
            #Sentences are separated by periods, question marks, and exclamation points followed by a space, single quote, or double
            sentence_regex = r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)(?=\s|'|\")"
            sentences = re.split(sentence_regex,article["text"][i])
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
        #Iterate through the questions and add an index to each question
        for i in range(len(article["questions"])):
            article["questions"][i]["index"] = i+1
        #Return the article title and the text as a list of paragraphs
        return render(request,'daily_article.html',{
            "title":article["title"],
            "paragraphs":paragraphs,
            "header":logged_in_header(),
            "w2s_map":w2s_map, 
            "questions":article["questions"], 
            "date":str(datetime.datetime.now().date())
            })
    else:
        return HttpResponseRedirect("/login/")
    
def add_points(request):
    #We need to extend the user model to include a points field
    #If the user is not logged in, return a 403 error
    if not request.user.is_authenticated:
        return HttpResponse(status=403)
    #Get the user object
    user = request.user
    u = auth.models.User.objects.get(username=user)
    #Get the number of points to add from the request
    #The request has JSON data with a key called points
    points = int(json.loads(request.body)["points"])
    #We're storing points in the last_name field for now
    if u.last_name == "":
        current_points = 0
    else:
        current_points = int(u.last_name)
    #Add the points to the user's points
    u.last_name = str(current_points + points)
    #Save the user object
    u.save()
    #Return the user's points
    #Content type is text
    return HttpResponse(u.last_name, content_type="text/plain")      

def submit_vocabulary(request):
    #Check if user is logged in
    if request.user.is_authenticated:
        #Get the request json data
        jsondata = json.loads(request.body)
        base_text = """
            Please provide your responses in the 4 line format below. Please do not write anything else so that I can parse this. I am giving you Spanishs word and the sentences they were used in. Please rewrite the word, tell me its base form, its translation in English, and an example sentence which uses the same meaning of the word but in at least a slightly different context. If multiple translations of the word are relevant to the sentence, you can provide the multiple translations separated by a comma. Please do not put more than 3 translations per word. If AND ONLY IF the word is a verb is used reflexively, please treat the base form as its reflexive form and make the translation for the reflexive verb. Please seperate your responses per word by a single line. Please only provide one response per word/sentence pair below.
            Word: 
            Base form: 
            Translation:
            Example sentence:
            Example translation:        
        """
        added_text = ""
        response_text = ""
        for i in range(len(jsondata)):
            added_text += "Word: "+jsondata[i]["word"]+"\n"
            added_text += "Sentence: "+jsondata[i]["sentence"]+"\n"
            if len(base_text) + len(added_text) > 10000 or i == len(jsondata)-1:
                # Use the new ChatCompletion.create method
                client = OpenAI(
                    # This is the default and can be omitted
                    api_key=os.environ.get('CHATGPT_KEY'),
                )

                response = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": base_text+added_text,
                        }
                    ],
                    model="gpt-3.5-turbo",
                )
                print(response)
                #Parse the response
                response_text += response.choices[0].message.content
                #Reset the added text
                added_text = ""

        #Split the response by line
        response_lines = response_text.split("\n")
        #Create a dictionary to hold the words and their data
        words = []
        for i in range(len(response_lines)):
            if response_lines[i][0:6] == "Word: ":
                word_dict = {"word": response_lines[i][6:].strip()}
            elif response_lines[i][0:11] == "Base form: ":
                word_dict["base"] = response_lines[i][11:].strip()
            elif response_lines[i][0:13] == "Translation: ":
                word_dict["translation"] = response_lines[i][13:].strip()
            elif response_lines[i][0:17] == "Example sentence:":
                word_dict["example"] = response_lines[i][17:].strip()
            elif response_lines[i][0:20] == "Example translation:":
                word_dict["example_translation"] = response_lines[i][20:].strip()
                words.append(word_dict)
        return HttpResponse(json.dumps(words), content_type="application/json")
    else:
        return HttpResponseRedirect("/login/")
    
def poetry(request):
    #Check if user is logged in
    if request.user.is_authenticated:
        return render(request,'poetry.html',{"header":logged_in_header()})
    else:
        return HttpResponseRedirect("/login/")