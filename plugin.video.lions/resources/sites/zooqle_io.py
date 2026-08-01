import re
import html
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
LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/zooqle_io.png'

SITE_IDENTIFIER = 'zooqle_io'
SITE_NAME = 'Zooqle'
SITE_DESC = 'Zooqle torrent site'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

CAT_FILMS = (URL_MAIN + '?category=movies&quality=all&genre=all&year=0&rating=0&language=all&sort_by=latest', 'showFilms')
CAT_SERIES = (URL_MAIN + '?category=tv&quality=all&genre=all&year=0&rating=0&language=all&sort_by=latest', 'showSeries')

URL_SEARCH = ('', 'showSearch')
FUNCTION_SEARCH = 'showSearch'
URL_SEARCH_DRAMAS = ('', 'showSearch')

def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search', icons + '/Search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', CAT_FILMS[0])
    oGui.addDir(SITE_IDENTIFIER, 'showFilms', 'Films', icons + '/Movies.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', CAT_SERIES[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'Series', icons + '/TVShows.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showSearch(sSearchText=''):
    oGui = cGui()
    if not sSearchText:
        sSearchText = oGui.showKeyBoard()
        if not sSearchText:
            oGui.setEndOfDirectory()
            return
    if sSearchText.startswith('http'):
        sUrl = sSearchText
    else:
        sSearchText = urllib.parse.unquote(sSearchText)
        sUrl = URL_MAIN + '?keyword=' + urllib.parse.quote(sSearchText) + '&quality=all&genre=all&year=0&rating=0&language=all&sort_by=latest'
        oRequestHandler = cRequestHandler(sUrl)
        sHtmlContent = oRequestHandler.request()
        __showTorrents(sHtmlContent)

def showFilms():
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    __showTorrents(sHtmlContent)

def showSeries():
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    __showTorrents(sHtmlContent)

def __showTorrents(sHtmlContent):
    oGui = cGui()
    oParser = cParser()

    sPattern = r'<div class="cell[^"]*">.*?<a href="(https://[^"]+/movies/[^"]+)"[^>]*title="([^"]+)"[^>]*>.*?<span class="browse-movie-year">([^<]*)</span>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sUrl = aEntry[0]
            sTitle = html.unescape(aEntry[1].strip()).replace('&#039;', "'").replace('&amp;', '&').replace('&quot;', '"')
            sYear = aEntry[2].strip()
            sDisplayName = sTitle + ' [COLOR grey]' + sYear + '[/COLOR]'

            oOutputParameterHandler.addParameter('siteUrl', sUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sDisplayName, icons + '/Movies.png', '', sDisplayName, oOutputParameterHandler)

    sNextPage = __checkForNextPage(sHtmlContent)
    if sNextPage:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sNextPage)
        oGui.addDir(SITE_IDENTIFIER, 'showFilms', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def __checkForNextPage(sHtmlContent):
    sPattern = r"<a title='next' href='([^']+)'\s*>"
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        sUrl = aResult[1][0]
        if sUrl.startswith('?'):
            sUrl = URL_MAIN.rstrip('/') + sUrl
        return sUrl
    return False

def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    oParser = cParser()

    sPattern = r'<td class="text-muted smaller"[^>]*>\d+\.</td>\s*<td class="text-nowrap text-trunc"[^>]*><a class="small "\s+href="(https://yts\.mx/torrent/download/([A-F0-9]+))"[^>]*>.*?<img[^>]*>([^<]+)</a>.*?<div class="progress-bar prog-blue prog-l"[^>]*>([^<]+)</div>.*?title="Seeders:\s*(\d+)\s*\|\s*Leechers:\s*(\d+)"'
    aResult = oParser.parse(sHtmlContent, sPattern)

    magnetAdded = False
    if aResult[0]:
        for aEntry in aResult[1]:
            torrentUrl = aEntry[0]
            infoHash = aEntry[1]
            sTitle = html.unescape(aEntry[2].strip())
            sSize = aEntry[3].strip()
            sSeeds = aEntry[4]
            sLeech = aEntry[5]

            magnetUrl = 'magnet:?xt=urn:btih:' + infoHash + '&dn=' + urllib.parse.quote(sTitle)
            encoded = urllib.parse.quote(magnetUrl, safe='')
            elementumUrl = 'plugin://plugin.video.elementum/play?uri=' + encoded

            sDisplayName = sTitle + ' [COLOR violet]Magnet[/COLOR] [' + sSize + '] S:' + sSeeds + ' L:' + sLeech

            oHoster = cHosterGui().getHoster('elementum')
            oHoster.setDisplayName(sDisplayName)
            oHoster.setFileName(sMovieTitle)
            cHosterGui().showHoster(oGui, oHoster, elementumUrl, '')
            magnetAdded = True

    if not magnetAdded:
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]No links found[/COLOR]')

    oGui.setEndOfDirectory()
