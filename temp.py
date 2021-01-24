import os
import sys
import boto3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR,'vitamova/scripts/'))
import ukrainian
import database as db

transcribe_level = 0

s3 = boto3.resource('s3')
object = s3.Object('wkbvitamova','transcribe/transcribe_embed.txt')
transcribe_srcs = object.get()['Body'].read()
transcribe_src = transcribe_srcs[transcribe_level]
object = s3.Object('wkbvitamova',"transcribe/transcribe_text_"+str(transcribe_level)+".txt")
transcription_content = object.get()['Body'].read()

print(transcribe_src)
print(transcription_content)