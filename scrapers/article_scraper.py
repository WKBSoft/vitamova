import requests
import re
import boto3

def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)
    
def remove_scripts(text):
    end_i = 0
    start_i = 0
    while start_i != -1:
        start_i = text.find("<script", end_i)
        end_i = text.find("</script",start_i)
        end_i = text.find(">", end_i) + 1
        if start_i != -1 and end_i != -1:
            text = text[0:start_i]+text[end_i:len(text)]
    return text

articles = []
links = [
    "https://ua.korrespondent.net/",
    "https://ua.korrespondent.net/ukraine/",
    "https://ua.korrespondent.net/city/kiev/",
    "https://ua.korrespondent.net/world/",
    "https://ua.korrespondent.net/business/",
    "https://ua.korrespondent.net/tech/",
    "https://ua.korrespondent.net/showbiz/",
    "https://ua.korrespondent.net/sport/",
    "https://ua.korrespondent.net/lifestyle/"
    ]
article_links = []
for x in links:
    main_content = requests.get(x).text
    con = True
    link_end = 0
    while con:
        link_start = main_content.find("<div class=\"article__title\">", link_end)
        if link_start==-1:
            con = False
        else:
            exact_start = main_content.find("href",link_start) +6
            link_end = main_content.find("\"",exact_start)
            link = main_content[exact_start:link_end]
            if link not in article_links:
                article_links.append(link)
for i in range(len(article_links)):
    article_content = requests.get(article_links[i]).text
    start_i = article_content.find("<div class=\"post-item__text\">")
    stop_i = article_content.find("<em>Новини від",start_i)
    article_content = article_content[start_i:stop_i]
    article_content = remove_scripts(article_content)
    article_content = remove_html_tags(article_content)
    article_content_bin = article_content.encode("utf-8")
    s3 = boto3.resource('s3')
    object = s3.Object('wkbvitamova', 'articles/'+str(i)+".txt")
    object.put(ACL='public-read',Body=article_content_bin)
    print(i,"/",len(article_links))
        
print("Done")
