import requests
import re
import boto3
import os
import datetime
from openai import OpenAI

import os

def source_profile(file_path):
    with open(file_path) as f:
        for line in f:
            if line.startswith('export '):
                # Strip out 'export ' and split by '=' to get the key and value
                key, value = line[len('export '):].strip().split('=', 1)
                # Remove surrounding quotes from value if they exist
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                os.environ[key] = value

# Use the function to source the profile
source_profile(os.path.expanduser("~/.profile"))

main_page = requests.get("https://laopinion.com/").text
start = main_page.find("portada__featured")
link_start = main_page.find("href",start) + 6
link_end = main_page.find("\"",link_start)
link = main_page[link_start:link_end]
article_page = requests.get(link).text
#The article title starts with the tag <h1 class="story__title">
title_start = article_page.find("<h1 class=\"story__title\">") + 25
title_end = article_page.find("</h1>",title_start)
title = article_page[title_start:title_end]
#Replace &#8221; with "
title = title.replace("&#8221;","\"")
#Replace &#8220; with "
title = title.replace("&#8220;","\"")
#The article text is scattered throughout the page, but it is all contained within the tag <p> which immediately follows a new line character
text = []
start = 0
while start != -1:
    start = article_page.find("\n<p>",start)
    if start != -1:
        end = article_page.find("</p>",start)
        sub_text = article_page[start+4:end]
        #Remove any html tags from the text
        clean = re.compile('<.*?>')
        sub_text = re.sub(clean, '', sub_text)
        #Replace &#8221; with "
        sub_text = sub_text.replace("&#8221;","\"")
        #Replace &#8220; with "
        sub_text = sub_text.replace("&#8220;","\"")
        #If the sub_text starts with Sigue leyendo:, set start to -1 to break the loop
        if sub_text.startswith("Sigue leyendo:"):
            start = -1
        else:
            text.append(sub_text)
            start = end

#Now we will use chatgpt to generate 5 multiple choice questions for the article
base_text = """
    Please provide 5 multiple choice questions for the following article. Please make sure that the questions are relevant to the article and that the correct answer is not too obvious. Please provide 4 answer choices for each question. Please do not write anything else and use exactly the below format so that I can parse this. 
    
    Example
    Question: What is the capital of France?
    Option 1: Washington
    Option 2: London
    Option 3: Paris
    Option 4: Moscow
    Correct answer: 3

    Article:
    """

condition = True

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get('CHATGPT_KEY'),
)

response = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": base_text + title + "\n" + "\n".join(text),
        }
    ],
    model="gpt-3.5-turbo",
)
print(response)
response_text = response.choices[0].message.content
response_lines = response_text.split("\n")

quiz_questions = []

for i in range(len(response_lines)):
    if response_lines[i].startswith("Question:"):
        question = response_lines[i][10:]
        option1 = response_lines[i+1][9:]
        option2 = response_lines[i+2][9:]
        option3 = response_lines[i+3][9:]
        option4 = response_lines[i+4][9:]
        correct_answer = response_lines[i+5][15:]
        quiz_questions.append({"question":question,"option1":option1,"option2":option2,"option3":option3,"option4":option4,"correct_answer":correct_answer})
        
    

#Make a json object with the title, text, and questions
article = {"title":title,"text":text,"questions":quiz_questions}
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
#Upload the article to the bucket called evenstarsec.vitamova
s3 = my_session.resource('s3')
#The filename will be today's date in the format YYYY-MM-DD.json
#It will be in the folder articles/spanish
#The body of the file will be the json object
filename = str(datetime.datetime.now().date())+".json"
s3.Bucket('evenstarsec.vitamova').put_object(Key="articles/spanish/"+filename,Body=str(article))