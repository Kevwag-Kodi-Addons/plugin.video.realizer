# -*- coding: utf-8 -*-
#

import xbmc
import xbmcgui
import xbmcaddon
import re
import sys
import logging

import six

if sys.version_info >= (2, 7):
    import json as json
else:
    import simplejson as json

# read settings
__addon__ = xbmcaddon.Addon('script.trakt')

logger = logging.getLogger(__name__)

REGEX_URL = '(^https?://)(.+)'

def notification(header, message, time=5000, icon=__addon__.getAddonInfo('icon')):
    xbmc.executebuiltin("XBMC.Notification(%s,%s,%i,%s)" % (header, message, time, icon))

def showSettings():
    __addon__.openSettings()

def getSetting(setting):
    if six.PY2:
        return __addon__.getSetting(setting).strip().decode('utf-8')
    else:
        return __addon__.getSetting(setting).strip()

def setSetting(setting, value):
    __addon__.setSetting(setting, str(value))

def getSettingAsBool(setting):
    return getSetting(setting).lower() == "true"

def getSettingAsFloat(setting):
    try:
        return float(getSetting(setting))
    except ValueError:
        return 0

def getSettingAsInt(setting):
    try:
        return int(getSettingAsFloat(setting))
    except ValueError:
        return 0

def getString(string_id):
    return __addon__.getLocalizedString(string_id).encode('utf-8', 'ignore')

def kodiJsonRequest(params):
    data = json.dumps(params)
    request = xbmc.executeJSONRPC(data)

    try:
        response = json.loads(request)
    except UnicodeDecodeError:
        response = json.loads(request.decode('utf-8', 'ignore'))

    try:
        if 'result' in response:
            return response['result']
        return None
    except KeyError:
        logger.warn("[%s] %s" % (params['method'], response['error']['message']))
        return None

# check exclusion settings for filename passed as argument


def kodiRpcToTraktMediaObjects(data, mode='collected'):
    if 'tvshows' in data:
        shows = data['tvshows']

        # reformat show array
        for show in shows:
            kodiRpcToTraktMediaObject('show', show, mode)
        return shows

    elif 'episodes' in data:
        a_episodes = {}
        seasons = []
        for episode in data['episodes']:
            while not episode['season'] in a_episodes:
                s_no = episode['season']
                a_episodes[s_no] = []
            s_no = episode['season']
            episodeObject = kodiRpcToTraktMediaObject('episode', episode, mode)
            if episodeObject:
                a_episodes[s_no].append(episodeObject)

        for episode in a_episodes:
            seasons.append({'number': episode, 'episodes': a_episodes[episode]})
        return seasons

    elif 'movies' in data:
        movies = data['movies']
        kodi_movies = []

        # reformat movie array
        for movie in movies:
            movieObject = kodiRpcToTraktMediaObject('movie', movie, mode)
            if movieObject:
                kodi_movies.append(movieObject)
        return kodi_movies
    else:
        logger.debug('kodiRpcToTraktMediaObjects() No valid key found in rpc data')
        return

def getShowDetailsFromKodi(showID, fields):
    result = kodiJsonRequest({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetTVShowDetails', 'params': {'tvshowid': showID, 'properties': fields}, 'id': 1})
    logger.debug("getShowDetailsFromKodi(): %s" % str(result))

    if not result:
        logger.debug("getShowDetailsFromKodi(): Result from Kodi was empty.")
        return None

    try:
        return result['tvshowdetails']
    except KeyError:
        logger.debug("getShowDetailsFromKodi(): KeyError: result['tvshowdetails']")
        return None

def getSeasonDetailsFromKodi(seasonID, fields):
    result = kodiJsonRequest({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetSeasonDetails', 'params': {'seasonid': seasonID, 'properties': fields}, 'id': 1})
    logger.debug("getSeasonDetailsFromKodi(): %s" % str(result))

    if not result:
        logger.debug("getSeasonDetailsFromKodi(): Result from Kodi was empty.")
        return None

    try:
        return result['seasondetails']
    except KeyError:
        logger.debug("getSeasonDetailsFromKodi(): KeyError: result['seasondetails']")
        return None

# get a single episode from kodi given the id
def getEpisodeDetailsFromKodi(libraryId, fields):
    result = kodiJsonRequest({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetEpisodeDetails', 'params': {'episodeid': libraryId, 'properties': fields}, 'id': 1})
    logger.debug("getEpisodeDetailsFromKodi(): %s" % str(result))

    if not result:
        logger.debug("getEpisodeDetailsFromKodi(): Result from Kodi was empty.")
        return None

    show_data = getShowDetailsFromKodi(result['episodedetails']['tvshowid'], ['year', 'imdbnumber'])

    if not show_data:
        logger.debug("getEpisodeDetailsFromKodi(): Result from getShowDetailsFromKodi() was empty.")
        return None

    result['episodedetails']['imdbnumber'] = show_data['imdbnumber']
    result['episodedetails']['year'] = show_data['year']

    try:
        return result['episodedetails']
    except KeyError:
        logger.debug("getEpisodeDetailsFromKodi(): KeyError: result['episodedetails']")
        return None

# get a single movie from kodi given the id
def getMovieDetailsFromKodi(libraryId, fields):
    result = kodiJsonRequest({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetMovieDetails', 'params': {'movieid': libraryId, 'properties': fields}, 'id': 1})
    logger.debug("getMovieDetailsFromKodi(): %s" % str(result))

    if not result:
        logger.debug("getMovieDetailsFromKodi(): Result from Kodi was empty.")
        return None

    try:
        return result['moviedetails']
    except KeyError:
        logger.debug("getMovieDetailsFromKodi(): KeyError: result['moviedetails']")
        return None

def checkAndConfigureProxy():
    proxyActive = kodiJsonRequest({'jsonrpc': '2.0', "method":"Settings.GetSettingValue", "params":{"setting":"network.usehttpproxy"}, 'id': 1})['value']
    proxyType = kodiJsonRequest({'jsonrpc': '2.0', "method":"Settings.GetSettingValue", "params":{"setting":"network.httpproxytype"}, 'id': 1})['value']

    if proxyActive and proxyType == 0: # PROXY_HTTP
        proxyURL = kodiJsonRequest({'jsonrpc': '2.0', "method":"Settings.GetSettingValue", "params":{"setting":"network.httpproxyserver"}, 'id': 1})['value']
        proxyPort = unicode(kodiJsonRequest({'jsonrpc': '2.0', "method":"Settings.GetSettingValue", "params":{"setting":"network.httpproxyport"}, 'id': 1})['value'])
        proxyUsername = kodiJsonRequest({'jsonrpc': '2.0', "method":"Settings.GetSettingValue", "params":{"setting":"network.httpproxyusername"}, 'id': 1})['value']
        proxyPassword = kodiJsonRequest({'jsonrpc': '2.0', "method":"Settings.GetSettingValue", "params":{"setting":"network.httpproxypassword"}, 'id': 1})['value']

        if proxyUsername and proxyPassword and proxyURL and proxyPort:
            regexUrl = re.compile(REGEX_URL)
            matchURL = regexUrl.search(proxyURL)
            if matchURL:
                return matchURL.group(1) + proxyUsername + ':' + proxyPassword + '@' + matchURL.group(2) + ':' + proxyPort
        elif proxyURL and proxyPort:
            return proxyURL + ':' + proxyPort

    return None

def getMediaType():
    if xbmc.getCondVisibility('Container.Content(tvshows)'):
        return "show"
    elif xbmc.getCondVisibility('Container.Content(seasons)'):
        return "season"
    elif xbmc.getCondVisibility('Container.Content(episodes)'):
        return "episode"
    elif xbmc.getCondVisibility('Container.Content(movies)'):
        return "movie"
    else:
        return None

