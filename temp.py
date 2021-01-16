import boto3
from random import randint
from random import shuffle

client = boto3.client('s3')
articles_list_r = client.list_objects_v2(Bucket='wkbvitamova',Prefix='articles/')
articles_list = articles_list_r['Contents']
selector = randint(0,len(articles_list)-1)
key = articles_list[selector]['Key']
s3 = boto3.resource('s3')
object = s3.Object('wkbvitamova',key)
article_content = object.get()['Body'].read().decode("utf-8")
response_l = article_content.split(" ")
shuffle(response_l)
response = "|".join(response_l[0:10])
print(response)