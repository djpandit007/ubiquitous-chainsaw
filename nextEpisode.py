from urllib2 import *
from bs4 import BeautifulSoup as bs
import re

def tvShowURL(tvShow):
    """
    Takes name of TV show as input and returns a formatted string
    which can be directly plugged into a URL
    """
    tvShow = tvShow.lower()
    tvShow = tvShow.replace("'", "")
    tvShow = tvShow.replace(' ', '-')
    return tvShow

def previousNext(tvShowFormatted):
    """
    Takes name of the TV show and returns dictionary about previous and next episodes
    If no serial is found, raises an exception
    """
    url = "http://next-episode.net/" + tvShowFormatted

    request = Request(url)
    response = urlopen(request)
    page = response.read()
    soup = bs(page, 'html.parser')

    previousEp = soup.find('div', {'id': 'previous_episode'}).text
    previousEp = previousEp.replace('Summary:Episode Summary', '').replace('\t', '').replace('\n\n', '\n')
    previousEp = previousEp.strip()
    name = re.findall(r'Name:(.*?)\nDate', previousEp)
    date = re.findall(r'Date:(.*?)\nSeason', previousEp)
    seasonNum = re.findall(r'Season:(.*?)\nEpisode', previousEp)
    episodeNum = re.findall(r'Episode:(.*?)$', previousEp)
    previousEpisode = {"episodeName": name, "airDate": date, "season": seasonNum, "episode": episodeNum, "text": previousEp}

    nextEp = soup.find('div', {'id': 'next_episode'}).text
    nextEp = nextEp.replace('Summary:Episode Summary', '').replace('\t', '').replace('\n\n', '\n')
    nextEp = nextEp.strip()
    name = re.findall(r'Name:(.*?)\nCountdown', nextEp)
    countdown = re.findall(r'Countdown:(.*?)\nDate', nextEp)
    date = re.findall(r'Date:(.*?)\nSeason', nextEp)
    seasonNum = re.findall(r'Season:(.*?)\nEpisode', nextEp)
    episodeNum = re.findall(r'Episode:(.*?)$', nextEp)
    misc = ''
    if name == date == countdown == seasonNum == episodeNum == []:
        misc = nextEp
    nextEpisode = {"episodeName": name, "airDate": date, "countDown": countdown, "season": seasonNum, "episode": episodeNum, "misc": misc, "text": nextEp}

    return {"previousEpisode": previousEpisode, "nextEpisode": nextEpisode}
