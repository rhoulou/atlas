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
LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/magnetdl_pro.png'

SITE_IDENTIFIER = 'magnetdl_pro'
SITE_NAME = 'MagnetDL'
SITE_DESC = 'MagnetDL torrent site'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

CAT_FILMS = (URL_MAIN + '/sort-movies-', 'showFilms')
CAT_SERIES = (URL_MAIN + '/sort-tv-', 'showSeries')

URL_SEARCH = (URL_MAIN + '/search?q=', 'showSearch')
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
        sUrl = URL_MAIN + '/search?q=' + urllib.parse.quote(sSearchText)
        oRequestHandler = cRequestHandler(sUrl)
        sHtmlContent = oRequestHandler.request()
        __showTorrents(sHtmlContent)
        oGui.setEndOfDirectory()

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

    sPattern = r'<div class="download">.*?<a href="(/[^"]+)"[^>]*>([^<]+)</a>.*?</div>.*?<span class="s[^"]*">(\d+)</span>.*?<span class="l[^"]*">(\d+)</span>.*?<span class="size[^"]*">([^<]+)</span>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if not aResult[0]:
        sPattern = r'<div class="download">.*?<a href="(/[^"]+)"[^>]*>([^<]+)</a>.*?<span class="s(\d+)"'
        aResult = oParser.parse(sHtmlContent, sPattern)

        if aResult[0]:
            oOutputParameterHandler = cOutputParameterHandler()
            for aEntry in aResult[1]:
                sUrl = aEntry[0]
                sTitle = html.unescape(aEntry[1].strip()).replace('&#039;', "'").replace('&amp;', '&').replace('&quot;', '"')
                sSeeds = aEntry[2].strip()
                sDisplayName = '{}\n[COLOR grey]Seeds: {}[/COLOR]'.format(sTitle, sSeeds)

                oOutputParameterHandler.addParameter('siteUrl', URL_MAIN.rstrip('/') + sUrl)
                oOutputParameterHandler.addParameter('sMovieTitle', sTitle)

                oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sDisplayName, icons + '/Movies.png', '', sDisplayName, oOutputParameterHandler)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sUrl = aEntry[0]
            sTitle = html.unescape(aEntry[1].strip()).replace('&#039;', "'").replace('&amp;', '&').replace('&quot;', '"')
            sSeeds = aEntry[2].strip()
            sLeech = aEntry[3].strip() if len(aEntry) > 3 else '0'
            sSize = aEntry[4].strip() if len(aEntry) > 4 else ''
            sDisplayName = '{}\n[COLOR grey]Size: {} | S:{} L:{}[/COLOR]'.format(sTitle, sSize, sSeeds, sLeech)

            oOutputParameterHandler.addParameter('siteUrl', URL_MAIN.rstrip('/') + sUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)

            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sDisplayName, icons + '/Movies.png', '', sDisplayName, oOutputParameterHandler)

    sNextPage = __checkForNextPage(sHtmlContent)
    if sNextPage:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sNextPage)
        oGui.addDir(SITE_IDENTIFIER, 'showFilms', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def __checkForNextPage(sHtmlContent):
    sPattern = r'<a href="([^"]+)"[^>]*>Next'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        return URL_MAIN.rstrip('/') + aResult[1][0]
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
        sPattern2 = r'href="(https?://[^"]+\.torrent)"'
        aResult2 = oParser.parse(sHtmlContent, sPattern2)
        if aResult2[0]:
            for torrentUrl in aResult2[1]:
                sTitle2 = sMovieTitle + ' [COLOR orange]Torrent[/COLOR]'
                oHoster2 = cHosterGui().checkHoster(torrentUrl)
                if oHoster2:
                    oHoster2.setDisplayName(sTitle2)
                    oHoster2.setFileName(sMovieTitle)
                    cHosterGui().showHoster(oGui, oHoster2, torrentUrl, '')

    if not magnetAdded:
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]No links found[/COLOR]')

    oGui.setEndOfDirectory()
