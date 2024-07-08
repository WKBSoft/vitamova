import requests
import json

def send(index, _id, data):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(data)
    x = requests.put("http://10.89.0.4:9200/"+index+"/_doc/"+_id,headers=headers,data=data)
    return x.text

def retrieve_all(index):
    x = requests.get("http://10.89.0.4:9200/"+index+"/_search")
    response = json.loads(x.text)
    hits = response['hits']['hits']
    result = {}
    for y in hits:
        result[y["_id"]] = y["_source"]
    return result
    
def retrieve(index,_id):
    x = requests.get("http://10.89.0.4:9200/"+index+"/_source/"+_id)
    response = json.loads(x.text)
    if "error" in response:
        response = {}
    return response

def delete(index):
    x = requests.delete("http://10.89.0.4:9200/"+index)
    response = json.loads(x.text)
    return response