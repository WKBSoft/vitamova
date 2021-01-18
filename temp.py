import boto3
import json

class user_data_c:
    def __init__(self,email):
        s3 = boto3.resource('s3')
        self.s3_object = s3.Object('wkbvitamova','users/userdata/'+email+'.json')
    def get(self):
        return json.load(self.s3_object.get()['Body'])
    def put(self,data):
        return self.s3_object.put(Body=json.dumps(data).encode("utf-8"))

x = user_data_c("bellemanwesley@gmail.com").get()
x["typing"]["level"] = "0"
x["points"] = 0
user_data_c("bellemanwesley@gmail.com").put(x)