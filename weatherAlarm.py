#!/usr/bin/python2.7
import requests
import json
import boto3
from datetime import datetime

def getApiKey():
    # Returns API Key for AccuWeather API
	try:
		credentials = open("AccuWeatherCredentials.txt", "r")
		apiKey = credentials.readline().strip()
		credentials.close()
		return apiKey
	except IOError:
		print "The file with weather credentials was not found!"

def getPhoneNumber():
    # Returns phone number as string
    try:
	contact = open("contact.txt", "r")
	mobilePhone = contact.readline().strip()
	contact.close()
	return mobilePhone
    except IOError:
	print "The file with contact details is not found"


locationKey = 336877
apiKey = getApiKey()
today = datetime.now().date()

weatherAlarmURL = "http://dataservice.accuweather.com/alarms/v1/1day/" + str(locationKey)

weatherAlarm = requests.get(weatherAlarmURL, params={"apikey": apiKey, "language": "en-us"})

alert = json.loads(weatherAlarm.content)
if alert:
    alert = alert[0]["Alarms"]
    alarmType = alert["AlarmType"]
    alarmValue, alarmUnit = alert["Value"]["Metric"]["Value"], alert["Value"]["Metric"]["Unit"]
    sns_client = boto3.client('sns', 'us-west-2')
    mobileNumber = getPhoneNumber()

    message = "Weather Alert Today!\nType: %s\nValue: %s %s" % (alarmType, alarmValue, alarmUnit)
    response = sns_client.publish(PhoneNumber=mobileNumber, Subject="Weather Alert", Message=message)
else:
    print str(today) + ": No weather alerts"
