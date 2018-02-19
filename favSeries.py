#!/usr/bin/python2.7
import MySQLdb
import yaml
from datetime import datetime
import json
import requests
import re
import boto3

todaysDate = str(datetime.now().date())
episodeToday = False
#sendMessage = "Series airing today:\n"
APIURL = "http://api.tvmaze.com"

def getFavSeries():
    try:
        with open("credentials.yml", "r") as ymlfile:
            fileContent = yaml.load(ymlfile)
        host = fileContent["host"]
        user = fileContent["user"]
        passwd = fileContent["passwd"]
        db = fileContent["db"]
        port = int(fileContent["port"])
        get_fav_series_sql = fileContent["get_fav_series_sql"]
    except IOError:
        print "The file with credentials was not found!"

    conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, port=port)
    cursor = conn.cursor()
    cursor.execute(get_fav_series_sql)
    results = cursor.fetchall()
    conn.close()
    ymlfile.close()
    return results

def getContactDetails():
    try:
        with open("credentials.yml", "r") as ymlfile:
            fileContent = yaml.load(ymlfile)
        mobileNumber = fileContent["phone-number"]
    except IOError:
        print "The file with contact details was not found!"
    return mobileNumber

def isEpisodeAiringToday(response):
    if "status" in response:
        if response["status"] == 404:
            return False
    else:
        return True

def getNameSummaryAirtime(content):
    return content["name"], content["summary"], content["airtime"]

def sanitize(text):
    return re.sub('<[^<]+?>', '', text).strip()

def sanitizeTitle(seriesName):
    seriesName = str(seriesName).replace("-", " ")
    seriesName = seriesName.title()
    return seriesName

def sendSMS(message):
    snsClient = boto3.client("sns", "us-west-2")
    mobileNumber = getContactDetails()
    response = snsClient.publish(PhoneNumber=mobileNumber, Message=message)



myFavourites = getFavSeries()

for seriesId, seriesName in myFavourites:
    response = requests.get(APIURL + "/shows/" + seriesId + "/episodesbydate?date=" + todaysDate)
    content = json.loads(response.content)
    if isEpisodeAiringToday(content):
        episodeToday = True
        epName, epSummary, airTime = getNameSummaryAirtime(content[0])
        epName, epSummary = sanitize(epName), sanitize(epSummary)
        #sendMessage += "%s airs at %s.\nEpisode Name: %s\nSummary: %s\n\n" % (str(sanitizeTitle(seriesName)), airTime, epName, epSummary)
        sendSMS("%s airs at %s.\nEpisode Name: %s\nSummary: %s\n\n" % (str(sanitizeTitle(seriesName)), airTime, epName, epSummary))
#if episodeToday:
#    sendSMS(sendMessage)
if not episodeToday:
    sendSMS("No series airing today")
