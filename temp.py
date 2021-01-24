import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR,'vitamova/scripts/'))
import ukrainian
import database as db

ua_text = '''
На цьому тижні президент США Джо Байден підписав 10 указів, спрямованих на розширення виробництва вакцин, прискорення тестування і повторне відкриття шкіл. "Будуть потрібні місяці, щоб все виправити", - сказав політик.
'''

response = ukrainian.replace_with_emphases(ua_text)
print(response)

#emphasis_request = db.retrieve("ukrainian_dict",)

#print(ukrainian.translate("привіт"))