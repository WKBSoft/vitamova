import requests
import boto3
import datetime
import os

#Get the website https://ua.korrespondent.net/
main_page = requests.get("https://ua.korrespondent.net/").text

#Start by finding the top news article which is under tag <div class="article article_top">
start = main_page.find("<div class=\"article article_top\">")
#Now find the link which follows <div class="article__title"><a href="
link_start = main_page.find("<div class=\"article__title\"><a href=\"",start) + 33
#The link ends with the next "
link_end = main_page.find("\"",link_start)

#Get the link to the article
link = main_page[link_start:link_end]
#Get the article page
article_page = requests.get(link).text
#The article title starts with the tag <h1 class="post-item__title">
title_start = article_page.find("<h1 class=\"post-item__title\">") + 29
title_end = article_page.find("</h1>",title_start)
title = article_page[title_start:title_end]

#The article text starts with the tag <div class="post-item__text">
text_start = article_page.find("<div class=\"post-item__text\">") + 28
#The article text ends with <em>
text_end = article_page.find("<em>",text_start)
text_raw = article_page[text_start:text_end]

text = []
start = 0
while start != -1:
    start = text_raw.find("\n<p>",start)
    if start != -1:
        end = text_raw.find("</p>",start)
        sub_text = text_raw[start+4:end]
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
    Please provide 5 multiple choice questions for the following article. 
    Please make sure that the questions are relevant to the article and that the correct answer is not too obvious. 
    Please provide 4 answer choices for each question. 
    Please do not write anything else and use exactly the below format so that I can parse this. 
    The questions and answers should be in ENGLISH. 
    
    Example
    Question: What is the capital of France?
    Option 1: Washington
    Option 2: London
    Option 3: Paris
    Option 4: Moscow
    Correct answer: 3

    AGAIN, EVEN THOUGH THE ARTICLE IS IN UKRAINIAN, THE QUESTIONS AND ANSWERS SHOULD BE IN ENGLISH!

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
    model="gpt-4o",
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

#Now we will upload the article and the quiz questions to the s3 bucket
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
s3.Bucket('evenstarsec.vitamova').put_object(Key="articles/uk/"+filename,Body=str(article))