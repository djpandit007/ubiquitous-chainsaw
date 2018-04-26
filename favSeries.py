#!/usr/bin/python2.7
# import MySQLdb
import yaml
from datetime import datetime
import json
import requests
import re
import boto3

todaysDate = str(datetime.now().date())
episodeToday = False
APIURL = "http://api.tvmaze.com"

"""
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
"""

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

def getSeasonEpisodeNumber(content):
    return int(content["season"]), int(content["number"])

def sanitize(text):
    if text:
        return re.sub('<[^<]+?>', '', text).strip()
    else:
        return ""

def sanitizeTitle(seriesName):
    seriesName = str(seriesName).replace("-", " ")
    seriesName = seriesName.title()
    return seriesName

def sendSMS(message):
    snsClient = boto3.client("sns", "us-west-2")
    mobileNumber = getContactDetails()
    response = snsClient.publish(PhoneNumber=mobileNumber, Message=message)

myFavourites = (
                ('66', 'the-big-bang-theory'),
                ('16579', 'the-handmaids-tale'),
                ('143', 'silicon-valley'),
                ('263', 'last-week-tonight-with-john-oliver'),
                ('1371', 'westworld'),
                ('335', 'sherlock'),
                ('3080', 'big-little-lies'),
                ('20596', 'splitting-up-together'),
                ('17128', 'this-is-us'),
#                ('7', 'homeland'),
                ('1804', 'the-man-in-the-high-castle'),
                ('2993', 'stranger-things'),
                ('80', 'modern-family'),
                ('82', 'game-of-thrones'),
                ('26020', 'young-sheldon')
                )

for seriesId, seriesName in myFavourites:
    response = requests.get(APIURL + "/shows/" + seriesId + "/episodesbydate?date=" + todaysDate)
    content = json.loads(response.content)
    if isEpisodeAiringToday(content):
        episodeToday = True
        for episode in content:
            epName, epSummary, airTime = getNameSummaryAirtime(episode)
            seasonNum, epNum = getSeasonEpisodeNumber(episode)
            epName, epSummary = sanitize(epName), sanitize(epSummary)
            sendSMS("%s S%02dE%02d airs at %s.\nEpisode Name: %s\nSummary: %s\n\n" % (str(sanitizeTitle(seriesName)), seasonNum, epNum, airTime, epName, epSummary))
if not episodeToday:
    sendSMS("No series airing today")
