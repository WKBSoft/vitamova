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
import urllib
import boto3
import json
import hashlib
import re

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR,'vitamova/scripts/'))
import ukrainian
import database as db

print(ukrainian.translate("привіт"))
