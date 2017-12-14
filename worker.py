import boto3
import pprint
import json
import requests

ACCESS_KEY = ""
SECRET_KEY = ""
REGION = ""


#body["TimezoneABBR"] = zipt['timezone']
#Get =SQS client
sqs = boto3.client('sqs',
    aws_access_key_id = ACCESS_KEY,
    aws_secret_access_key = SECRET_KEY,
    region_name = REGION
)

#Get the queue url
queue = sqs.get_queue_url(QueueName='cs415_jobs')
url = queue['QueueUrl']
# print(url)

#Receive message from SQS queue
response = sqs.receive_message(
    QueueUrl=url
)

message = response['Messages'][0]['Body']
#print(message)
mes = response['Messages'][0]
receipt_handle = mes['ReceiptHandle']

body = json.loads(message)
phone = body['Phone']

#Edit the phone
phone = phone.split('-')
p = ""
phoneNumber = p.join(phone)
body['Phone'] = phoneNumber
#print phoneNumber

body['_worker'] = "binPin"
#print body

#Extra timezone
zipTime = body['Zip']
zipt = requests.get('https://www.zipcodeapi.com/rest/dzduXWsXOt2ToXogkv2ErBTZWbVXvDTCscQxibWrTFDNraDoFIhMVpO1Q5y0a0cN/info.json/'+zipTime+'/degrees')
#print zipt.json()
body['TimezoneABBR'] = zipt.json()['timezone']['timezone_abbr']
print body

#Extra temparature
zipCode = body['Zip']
temp = requests.get('https://api.openweathermap.org/data/2.5/weather?zip='+str(zipCode)+',us&APPID=46476857c95c8709982f54fdb41e6001')
body['Temperature_F'] = temp.json()['main']['temp'] * 9.0 /5.0 - 459.67
print body


#Send the queue
queue = sqs.get_queue_url(QueueName='cs415_results')
sendUrl = queue['QueueUrl']
#Send message to SQS queue
response = sqs.send_message(
    QueueUrl=sendUrl,
    MessageBody = json.dumps(body)
)

#Delete
sqs.delete_message(
    QueueUrl = url,
    ReceiptHandle=receipt_handle
)
