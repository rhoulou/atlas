# -*- coding: utf-8 -*-
import re
import requests
import urllib.parse

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.comaddon import VSlog, siteManager, addon

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/youtube.png'

SITE_IDENTIFIER = 'youtube'
SITE_NAME = 'YouTube'
SITE_DESC = 'youtube search'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

URL_SEARCH_MOVIES = ('', 'showSearch')
URL_SEARCH_DRAMAS = ('', 'showSearch')
URL_SEARCH_SERIES = ('', 'showSearchSeries')

SEARCH_URL = 'https://www.youtube.com/results'
WATCH_URL = 'https://www.youtube.com/watch?v='

MIN_MOVIE_DURATION = 1800

sUserAgent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36'


def _normalize(sText):
    aWords = []
    for sWord in re.split(r'(\W+)', sText.lower()):
        sWord = re.sub(r'(.)\1+', r'\1', sWord)
        if sWord.endswith('y'):
            sWord = sWord[:-1] + 'i'
        aWords.append(sWord)
    return ''.join(aWords)


def _searchKeywords(sQuery):
    return [_normalize(w) for w in sQuery.split() if not re.match(r'^\d{4}$', w)]


def _matchesTitle(sTitle, aKeywords):
    if not aKeywords:
        return True
    sTitleNorm = _normalize(sTitle)
    return all(w in sTitleNorm for w in aKeywords)


def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search', icons + '/Search.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showSearch(sSearchText=''):
    __search(sSearchText, True)


def showSearchSeries(sSearchText=''):
    __search(sSearchText, False)


def __search(sSearchText, bMinDuration):
    oGui = cGui()

    bFromMenu = not sSearchText
    if bFromMenu:
        sSearchText = oGui.showKeyBoard()
        if not sSearchText:
            oGui.setEndOfDirectory()
            return False

    sSearchText = urllib.parse.unquote(sSearchText)
    aKeywords = _searchKeywords(sSearchText)
    aResults = []
    try:
        for aEntry in __searchYoutube(sSearchText):
            if not _matchesTitle(aEntry['title'], aKeywords):
                continue
            if bMinDuration and aEntry['duration'] < MIN_MOVIE_DURATION:
                continue
            aResults.append(aEntry)
    except Exception as e:
        VSlog('youtube: search failed (' + str(e) + ')')

    if not aResults:
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]No results[/COLOR]')

    for aEntry in aResults:
        sTitle = aEntry['title'].strip()
        sThumb = aEntry['thumb']
        sIcon = sThumb if sThumb else icons + '/Movies.png'
        sMin = int(aEntry['duration'] / 60)
        if sMin > 0:
            sDisplay = '%s [COLOR grey][%dmin][/COLOR] [COLOR violet]%s[/COLOR]' % (sTitle, sMin, aEntry['host'])
        else:
            sDisplay = '%s [COLOR violet]%s[/COLOR]' % (sTitle, aEntry['host'])

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', aEntry['url'])
        oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
        oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sDisplay, sIcon, sThumb, sDisplay, oOutputParameterHandler)

    if bFromMenu:
        oGui.setEndOfDirectory()


def __searchYoutube(sQuery):
    aResults = []
    oSession = requests.Session()
    oSession.headers.update({'User-Agent': sUserAgent, 'Accept-Language': 'en-US,en;q=0.9'})
    oResponse = oSession.get(SEARCH_URL, params={'search_query': sQuery}, timeout=15)
    sHtmlContent = oResponse.text

    oMatch = re.search(r'var ytInitialData = ({.*?});</script>', sHtmlContent, re.S)
    if not oMatch:
        return aResults

    import json
    oData = json.loads(oMatch.group(1))
    aVideos = []

    def __walk(oNode):
        if isinstance(oNode, dict):
            if 'videoRenderer' in oNode:
                oVideo = oNode['videoRenderer']
                sId = oVideo.get('videoId', '')
                if not sId:
                    return
                sTitle = ''.join(t.get('text', '') for t in oVideo.get('title', {}).get('runs', []))
                sLength = oVideo.get('lengthText', {}).get('simpleText', '')
                sThumb = ''
                try:
                    sThumb = oVideo['thumbnail']['thumbnails'][-1]['url']
                except Exception:
                    pass
                aVideos.append((sId, sTitle, sLength, sThumb))
            for oValue in oNode.values():
                __walk(oValue)
        elif isinstance(oNode, list):
            for oItem in oNode:
                __walk(oItem)

    __walk(oData)

    for sId, sTitle, sLength, sThumb in aVideos:
        aResults.append({'host': 'YOUTUBE', 'url': WATCH_URL + sId,
                         'title': sTitle, 'duration': __toSeconds(sLength), 'thumb': sThumb})
    return aResults


def __toSeconds(sLength):
    if not sLength:
        return 0
    aParts = sLength.split(':')
    iTotal = 0
    for i, sPart in enumerate(reversed(aParts)):
        try:
            iTotal += int(sPart) * 60 ** i
        except ValueError:
            return 0
    return iTotal


def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')

    sEmbedUrl = sUrl.split('|')[0]
    oHoster = cHosterGui().checkHoster(sEmbedUrl)

    if oHoster:
        oHoster.setDisplayName(sMovieTitle)
        oHoster.setFileName(sMovieTitle)
        cHosterGui().showHoster(oGui, oHoster, sEmbedUrl, '')

    oGui.setEndOfDirectory()
