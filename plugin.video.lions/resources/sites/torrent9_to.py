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
LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/torrent9_to.png'

SITE_IDENTIFIER = 'torrent9_to'
SITE_NAME = 'Torrent9 (.to)'
SITE_DESC = 'Torrent9 torrent site on torrent9.to'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

CAT_FILMS = (URL_MAIN + '/torrents_films.html', 'showFilms')
CAT_SERIES = (URL_MAIN + '/torrents_series.html', 'showSeries')

URL_SEARCH = (URL_MAIN + 'search_torrent/', 'showSearch')
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
        sUrl = URL_MAIN + 'search_torrent/' + urllib.parse.quote(urllib.parse.unquote(sSearchText))
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    __showTorrents(sHtmlContent, sUrl)

def showFilms():
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    __showTorrents(sHtmlContent, sUrl)

def showSeries():
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    __showTorrents(sHtmlContent, sUrl)

def __showTorrents(sHtmlContent, sUrl=''):
    oGui = cGui()
    sHtmlContent = re.sub(r'\r?\n\s*', '', sHtmlContent)
    oParser = cParser()

    sPattern = r'<a title="([^"]+)" href="(/torrent/\d+/[^"]+)"[^>]*>.*?</a></td><td[^>]*>[^<]*</td><td[^>]*>([^<]+)</td><td[^>]*><span class="seed_ok">\s*(\d+)'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sTitle = aEntry[0].strip().replace('&#039;', "'").replace('&amp;', '&').replace('&quot;', '"')
            sDetailUrl = aEntry[1]
            sSize = aEntry[2].strip()
            sSeeds = aEntry[3].strip()
            sDisplayName = '{}\n[COLOR grey]Size: {} | Seeds: {}[/COLOR]'.format(sTitle, sSize, sSeeds)

            oOutputParameterHandler.addParameter('siteUrl', URL_MAIN.rstrip('/') + sDetailUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)

            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sDisplayName, icons + '/Movies.png', '', sDisplayName, oOutputParameterHandler)

    sNextPage = __checkForNextPage(sHtmlContent, sUrl)
    if sNextPage:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sNextPage)
        oGui.addDir(SITE_IDENTIFIER, 'showSearch', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def __checkForNextPage(sHtmlContent, sUrl=''):
    if not sUrl:
        return False
    oMatch = re.search(r'(?:/|,)page-(\d+)$', sUrl)
    iCurrent = int(oMatch.group(1)) if oMatch else 1
    aPages = []
    for oMatch in re.finditer(r'<li[^>]*><a[^>]*>\s*(\d+)\s*</a></li>', sHtmlContent):
        aPages.append(int(oMatch.group(1)))
    if not aPages:
        return False
    if iCurrent >= max(aPages):
        return False
    if '/search_torrent/' in sUrl:
        return re.sub(r'/page-\d+$', '', sUrl) + '/page-' + str(iCurrent + 1)
    return re.sub(r',page-\d+$', '', sUrl) + ',page-' + str(iCurrent + 1)

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
        sPattern2 = r'href="(/[^"]+\.torrent)"'
        aResult2 = oParser.parse(sHtmlContent, sPattern2)
        if aResult2[0]:
            for torrentPath in aResult2[1]:
                fullUrl = URL_MAIN.rstrip('/') + torrentPath
                sTitle2 = sMovieTitle + ' [COLOR orange]Torrent[/COLOR]'
                oHoster2 = cHosterGui().checkHoster(fullUrl)
                if oHoster2:
                    oHoster2.setDisplayName(sTitle2)
                    oHoster2.setFileName(sMovieTitle)
                    cHosterGui().showHoster(oGui, oHoster2, fullUrl, '')

    oGui.setEndOfDirectory()
