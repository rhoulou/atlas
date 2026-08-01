import re
import html
import json
import urllib.parse

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import VSlog, siteManager, addon

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/en_yts_lu.png'

SITE_IDENTIFIER = 'en_yts_lu'
SITE_NAME = 'en.yts.lu'
SITE_DESC = 'YTS torrent site alternate'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

URL_SEARCH = ('', 'showSearch')
FUNCTION_SEARCH = 'showSearch'

def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search', icons + '/Search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '?api=popular&mode=movie&page=1')
    oGui.addDir(SITE_IDENTIFIER, 'showFilms', 'Films', icons + '/Movies.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '?api=popular&mode=tv&page=1')
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'Series', icons + '/TVShows.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showSearch(sSearchText=''):
    oGui = cGui()
    if not sSearchText:
        sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = URL_MAIN + '?api=search&mode=movie&q=' + urllib.parse.quote(sSearchText) + '&page=1'
        oRequestHandler = cRequestHandler(sUrl)
        sJsonContent = oRequestHandler.request()
        __showTorrents(sJsonContent, 'movie')
        oGui.setEndOfDirectory()

def showFilms():
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    oRequestHandler = cRequestHandler(sUrl)
    sJsonContent = oRequestHandler.request()
    __showTorrents(sJsonContent, 'movie')

def showSeries():
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    oRequestHandler = cRequestHandler(sUrl)
    sJsonContent = oRequestHandler.request()
    __showTorrents(sJsonContent, 'tv')

def __showTorrents(sJsonContent, sMode):
    oGui = cGui()
    oParser = cParser()

    try:
        data = json.loads(sJsonContent)
    except:
        oGui.setEndOfDirectory()
        return

    isMovie = sMode == 'movie'
    results = data.get('results', [])

    if results:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in results:
            if isMovie:
                sTitle = aEntry.get('title', '')
                sYear = aEntry.get('release_date', '')[:4]
            else:
                sTitle = aEntry.get('name', '')
                sYear = aEntry.get('first_air_date', '')[:4]

            if not sTitle:
                continue

            sDisplayName = sTitle + ' [COLOR grey]' + sYear + '[/COLOR]'

            if isMovie:
                sTorrentUrl = URL_MAIN + '?api=torrents&mode=movie&name=' + urllib.parse.quote(sTitle) + '&year=' + urllib.parse.quote(sYear) + '&quality=all'
            else:
                sTorrentUrl = URL_MAIN + '?api=torrents&mode=tv&name=' + urllib.parse.quote(sTitle) + '&quality=all'

            oOutputParameterHandler.addParameter('siteUrl', sTorrentUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)

            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sDisplayName, icons + '/Movies.png', '', sDisplayName, oOutputParameterHandler)

    sNextPage = __checkForNextPage(data, sMode)
    if sNextPage:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sNextPage)
        sNextFunction = 'showFilms' if isMovie else 'showSeries'
        oGui.addDir(SITE_IDENTIFIER, sNextFunction, '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def __checkForNextPage(data, sMode):
    page = data.get('page', 1)
    totalPages = data.get('total_pages', 1)
    if page < totalPages:
        nextPage = page + 1
        return URL_MAIN + '?api=popular&mode=' + sMode + '&page=' + str(nextPage)
    return False

def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')

    if not sUrl:
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]No links found[/COLOR]')
        oGui.setEndOfDirectory()
        return

    oRequestHandler = cRequestHandler(sUrl)
    sJsonContent = oRequestHandler.request()

    try:
        data = json.loads(sJsonContent)
    except:
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]No links found[/COLOR]')
        oGui.setEndOfDirectory()
        return

    hits = data.get('hits', [])

    magnetAdded = False
    for hit in hits:
        magnetUrl = hit.get('magnetUrl', '')
        if not magnetUrl:
            continue

        sTitle = hit.get('title', sMovieTitle)
        sSeeds = str(hit.get('seeds', 0))
        sLeech = str(hit.get('peers', 0))
        sBytes = hit.get('bytes', 0)
        if sBytes:
            sSize = '{:.2f} GB'.format(sBytes / (1024**3)) if sBytes > 1024**3 else '{:.2f} MB'.format(sBytes / (1024**2))
        else:
            sSize = ''

        encoded = urllib.parse.quote(magnetUrl, safe='')
        elementumUrl = 'plugin://plugin.video.elementum/play?uri=' + encoded

        sDisplayName = sTitle[:80] + ' [COLOR violet]Magnet[/COLOR] [' + sSize + '] S:' + sSeeds + ' L:' + sLeech

        oHoster = cHosterGui().getHoster('elementum')
        oHoster.setDisplayName(sDisplayName)
        oHoster.setFileName(sMovieTitle)
        cHosterGui().showHoster(oGui, oHoster, elementumUrl, '')
        magnetAdded = True

    if not magnetAdded:
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]No links found[/COLOR]')

    oGui.setEndOfDirectory()
