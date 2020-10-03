# coding=utf-8
from django.shortcuts import render
from django.http import HttpResponse
import sys
import urllib
import boto3
sys.path.insert(0, '/home/ubuntu/vitamova/vitamova/localviews/')
import ukrainian
import content_gen
#translate_key = urllib.parse.unquote(request.GET.get('translate',""))


def get_s3_content(key):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('wkbvitamova')
    obj = bucket.Object(key)
    file_data = obj.get()
    return file_data['Body'].read().decode('utf-8')
get_s3_content('home_content.html')
'''
def get_book():
    book_title = urllib.parse.unquote("Сицилієць%20-%20Маріо%20П’юзо.fb2")
    book_page = "3"
    file_data = content_gen.get_s3_content('books/'+book_title)
    book_pages = urllib.parse.quote(ukrainian.return_pages(file_data,200,book_page))
    return book_pages

print(get_book())'''