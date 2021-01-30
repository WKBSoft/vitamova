#test

import os
import sys
import boto3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR,'vitamova/scripts/'))
import ukrainian
import database as db

print(ukrainian.translate("привіт"))
