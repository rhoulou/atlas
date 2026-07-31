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
LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/dailymotion.png'

SITE_IDENTIFIER = 'dailymotion'
SITE_NAME = 'Dailymotion'
SITE_DESC = 'dailymotion search'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

URL_SEARCH_MOVIES = ('', 'showSearch')
URL_SEARCH_DRAMAS = ('', 'showSearch')
URL_SEARCH_SERIES = ('', 'showSearchSeries')

DM_API = 'https://api.dailymotion.com/videos'

MIN_MOVIE_DURATION = 1800


def _searchKeywords(sQuery):
    return [w.lower() for w in sQuery.split() if not re.match(r'^\d{4}$', w)]


def _matchesTitle(sTitle, aKeywords):
    if not aKeywords:
        return True
    sTitleLower = sTitle.lower()
    return all(w in sTitleLower for w in aKeywords)


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
        for aEntry in __searchDailymotion(sSearchText):
            if not _matchesTitle(aEntry['title'], aKeywords):
                continue
            if bMinDuration and aEntry['duration'] < MIN_MOVIE_DURATION:
                continue
            aResults.append(aEntry)
    except Exception as e:
        VSlog('dailymotion: search failed (' + str(e) + ')')

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


def __searchDailymotion(sQuery):
    aResults = []
    oResponse = requests.get(DM_API, params={'search': sQuery, 'fields': 'id,title,duration,thumbnail_720_url', 'limit': '25'}, timeout=15)
    for oVideo in oResponse.json().get('list', []):
        sId = oVideo.get('id', '')
        if not sId:
            continue
        aResults.append({'host': 'DAILYMOTION', 'url': 'https://www.dailymotion.com/embed/video/' + sId,
                         'title': oVideo.get('title', '?'), 'duration': int(oVideo.get('duration', 0)),
                         'thumb': oVideo.get('thumbnail_720_url', '')})
    return aResults


def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')

    sEmbedUrl = sUrl.split('|')[0]
    oHoster = None
    try:
        import resolveurl
        oHmf = resolveurl.HostedMediaFile(url=sEmbedUrl)
        if oHmf.valid_url():
            oHoster = cHosterGui().getHoster('resolver')
            sHost = sEmbedUrl.split('/')[2].replace('www.', '').split('.')[0].upper()
            oHoster.setRealHost(sHost)
    except Exception:
        pass

    if not oHoster:
        oHoster = cHosterGui().checkHoster(sEmbedUrl)

    if oHoster:
        oHoster.setDisplayName(sMovieTitle)
        oHoster.setFileName(sMovieTitle)
        cHosterGui().showHoster(oGui, oHoster, sEmbedUrl, '')

    oGui.setEndOfDirectory()
