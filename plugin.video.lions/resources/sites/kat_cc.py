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

SITE_IDENTIFIER = 'kat_cc'
SITE_NAME = 'KAT'
SITE_DESC = 'KickAss Torrents'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

_KAT_BASE = None

def __getWorkingMirror():
    global _KAT_BASE
    if _KAT_BASE:
        return _KAT_BASE

    mirrors = ['https://kickasstorrents.cc']

    try:
        oReq = cRequestHandler(URL_MAIN)
        oReq.setTimeout(10)
        htmlContent = oReq.request()
        if htmlContent:
            oParser = cParser()
            sPattern = r'<a class="domainLink" href="(https://[^"]+)"'
            aResult = oParser.parse(htmlContent, sPattern)
            if aResult[0]:
                for url in aResult[1]:
                    url = url.rstrip('/')
                    if url not in mirrors:
                        mirrors.append(url)
    except:
        pass

    for mirror in mirrors:
        try:
            testUrl = mirror + '/browse/all'
            oTest = cRequestHandler(testUrl)
            oTest.setTimeout(10)
            content = oTest.request()
            if content and 'cellMainLink' in content:
                _KAT_BASE = mirror
                return mirror
        except:
            continue

    _KAT_BASE = 'https://kickasstorrents.cc'
    return _KAT_BASE


def load():
    oGui = cGui()
    base = __getWorkingMirror()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search', icons + '/Search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', base + '/browse/movies')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'Movies', icons + '/Movies.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', base + '/browse/tv')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'TV', icons + '/TVShows.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', base + '/popular/movies')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'Popular Movies', icons + '/Movies.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', base + '/popular/tv')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'Popular TV', icons + '/TVShows.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = __getWorkingMirror() + '/search?query=' + urllib.parse.quote(sSearchText)
        showMovies(sUrl)
        oGui.setEndOfDirectory()


def showMovies(sSearch=''):
    oGui = cGui()
    oParser = cParser()

    if sSearch:
        sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = r'<tr class="even">.*?<a href="(https://[^"]+/torrent/\d+)" class="cellMainLink">([^<]+)</a>.*?</td>.*?<td class="nobr center[^"]*"[^>]*>([^<]+)</td>.*?<td class="green center">(\d+)</td>.*?<td class="red lasttd center">(\d+)</td>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sUrl = aEntry[0]
            sTitle = aEntry[1].strip()
            sSize = aEntry[2].strip()
            sSeeds = aEntry[3].strip()
            sLeech = aEntry[4].strip()
            sDisplayName = '{}\n[COLOR grey]Size: {} | S:{} L:{}[/COLOR]'.format(sTitle, sSize, sSeeds, sLeech)

            oOutputParameterHandler.addParameter('siteUrl', sUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)

            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sDisplayName, icons + '/Movies.png', '', sDisplayName, oOutputParameterHandler)

    sNextPage = __checkForNextPage(sHtmlContent)
    if sNextPage:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sNextPage)
        oGui.addDir(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    if not sSearch:
        oGui.setEndOfDirectory()


def __checkForNextPage(sHtmlContent):
    oParser = cParser()
    sPattern = r'<a class="turnoverButton siteButton bigButton" href="([^"]+)" rel="next">>></a>'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        return aResult[1][0]
    return False


def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    oParser = cParser()

    sPattern = r'href="(magnet:[^"]+)"'
    aResult = oParser.parse(sHtmlContent, sPattern)

    magnetAdded = False
    if aResult[0]:
        for magnetUrl in aResult[1]:
            magnetUrl = html.unescape(magnetUrl)
            encoded = urllib.parse.quote(magnetUrl, safe='')
            elementumUrl = 'plugin://plugin.video.elementum/play?uri=' + encoded
            sTitle = sMovieTitle + ' [COLOR violet]Magnet[/COLOR]'

            oHoster = cHosterGui().getHoster('elementum')
            oHoster.setDisplayName(sTitle)
            oHoster.setFileName(sMovieTitle)
            cHosterGui().showHoster(oGui, oHoster, elementumUrl, '')
            magnetAdded = True

    if not magnetAdded:
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]No links found[/COLOR]')

    oGui.setEndOfDirectory()
