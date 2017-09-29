#!/usr/bin/python2.7
import requests
import json
import boto3
import yaml
from datetime import datetime

def getApiKey():
    # Returns API Key for AccuWeather API
    try:
        with open("credentials.yml", "r") as ymlfile:
            fileContent = yaml.load(ymlfile)
	apiKey = fileContent["accuweather-key"].strip()
	ymlfile.close()
	return apiKey
    except IOError:
	print "The file with weather credentials was not found!"

def getPhoneNumber():
    # Returns phone number as string
    try:
        with open("credentials.yml", "r") as ymlfile:
            fileContent = yaml.load(ymlfile)
	mobilePhone = str(fileContent["phone-number"]).strip()
	ymlfile.close()
	return mobilePhone
    except IOError:
	print "The file with contact details is not found"

locationKey = 336877
apiKey = getApiKey()
today = datetime.now().date()

weatherForecastURL = "http://dataservice.accuweather.com/forecasts/v1/daily/1day/" + str(locationKey)
weatherForecast = requests.get(weatherForecastURL, params={"apikey": apiKey, "language": "en-us", "details": True, "metric": True})
response = json.loads(weatherForecast.content)

message = str(datetime.now().strftime("%A, %d %B %Y"))
message += "\nWeather Severity: "

severity = int(response["Headline"]["Severity"])

if severity <= 3:
    message += "High\n"
elif 4 <= severity <= 7:
    message += "Medium\n"
else:
    message += "Low\n"

headline = response["Headline"]["Text"]
message += headline + "\n"

dailyForecast = response["DailyForecasts"][0]
maxTemp = dailyForecast["RealFeelTemperature"]["Maximum"]
minTemp = dailyForecast["RealFeelTemperature"]["Minimum"]
uvIndex = str(dailyForecast["AirAndPollen"][-1]["Category"])

message += "Temp range: " + str(minTemp["Value"]) + " to " + str(maxTemp["Value"]) + " " + str(maxTemp["Unit"]) + "\n"
message += "UV Index: " + uvIndex + "\n"

message += "\nMorning: "

day = dailyForecast["Day"]
dayShort = str(day["ShortPhrase"])
dayWind = day["Wind"]["Speed"]
dayRain = day["Rain"]
daySnow = day["Snow"]
dayIce = day["Ice"]

message += dayShort + "\n"
message += "Wind: " + str(dayWind["Value"]) + str(dayWind["Unit"]) + "  "
message += "Rain: " + str(dayRain["Value"]) + str(dayRain["Unit"]) + "  "
message += "Snow: " + str(daySnow["Value"]) + str(daySnow["Unit"]) + "  "
message += "Ice: " + str(dayIce["Value"]) + str(dayIce["Unit"]) + "  \n"

message += "\nNight: "

night = dailyForecast["Night"]
nightShort = str(night["ShortPhrase"])
nightWind = night["Wind"]["Speed"]
nightRain = night["Rain"]
nightSnow = night["Snow"]
nightIce = night["Ice"]

message += nightShort + "\n"
message += "Wind: " + str(nightWind["Value"]) + str(nightWind["Unit"]) + "  "
message += "Rain: " + str(nightRain["Value"]) + str(nightRain["Unit"]) + "  "
message += "Snow: " + str(nightSnow["Value"]) + str(nightSnow["Unit"]) + "  "
message += "Ice: " + str(nightIce["Value"]) + str(nightIce["Unit"]) + "  "

sns_client = boto3.client("sns", "us-west-2")
mobileNumber = getPhoneNumber()
smsResponse = sns_client.publish(PhoneNumber=mobileNumber, Subject="Weather Forecast", Message=message)
print str(today) + ". " + str(smsResponse["ResponseMetadata"]["HTTPStatusCode"]) 
