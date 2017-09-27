#!/usr/bin/python2.7
import TheTvDbEpisode
import nextEpisode
import sys
import json
from datetime import datetime


sendMessage = "Here are the series airing today (ET).\n"
episodeToday = False
myFavouries = TheTvDbEpisode.getMyFavorites()
token = TheTvDbEpisode.authenticate()
todaysDate = datetime.now().date()

for series in myFavouries:
    try:
        seriesName, seriesTime = TheTvDbEpisode.getSeriesNameTime(series)
        seriesNameFormatted = nextEpisode.tvShowURL(seriesName)
        latestEpisodes = nextEpisode.previousNext(seriesNameFormatted)
        later = latestEpisodes["nextEpisode"]
        nextAirDate = later["airDate"]
        if nextAirDate:
            nextAirDateFormatted = datetime.strptime(nextAirDate[0], '%a %b %d, %Y').date()
            if nextAirDateFormatted == todaysDate:
                episodeToday = True
                sendMessage += "%s airs at %s in %s\n" % (str(seriesName), str(seriesTime), str(later["countDown"][0]))
    except Exception as err:
	print "Exception occured for %s: %s" % (seriesName, err)



print "CRON job date: " + str(todaysDate)
if episodeToday:
    TheTvDbEpisode.sendSMS(sendMessage)
else:
    TheTvDbEpisode.sendSMS("No series airing today")
