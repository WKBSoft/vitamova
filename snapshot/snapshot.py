DB_URL = "http://10.89.0.4:9200/"

import requests
import json
from time import sleep

print("start")

def register():
    doc = {
        "type": "s3",
        "settings": {
            "bucket": "wkbvitamova"
        }
    }
    data = json.dumps(doc)
    response = requests.put(DB_URL + '_snapshot/my_s3_repository', data=data, headers={'Content-Type':'application/json'})
    response_json = json.loads(response.text)
    return response_json

con = True
while con:
    try:
        register_response = register()
        print(register_response)
        if "error" not in register_response:
            con = False
        else:
            sleep(5)
    except:
        sleep(5)

print(requests.post(DB_URL + '_snapshot/my_s3_repository/1/_restore').text)

i = 0

while True:
    sleep(300)
    print(requests.delete(DB_URL+'_snapshot/my_s3_repository/'+str(i+1)).text)
    print(requests.put(DB_URL+'_snapshot/my_s3_repository/'+str(i+1)).text)
    i = (i+1)%2
