import requests
import re
import boto3
import os
import datetime

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

#Make a json object with the title and text
article = {"title":title,"text":text}
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
filename = str(datetime.date.today())+".json"
s3.Bucket('evenstarsec.vitamova').put_object(Key="articles/spanish/"+filename,Body=str(article))