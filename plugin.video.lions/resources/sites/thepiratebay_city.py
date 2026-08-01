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
LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/thepiratebay_city.png'

SITE_IDENTIFIER = 'thepiratebay_city'
SITE_NAME = 'The Pirate Bay'
SITE_DESC = 'The Pirate Bay torrent site'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

CAT_FILMS = (URL_MAIN + 'search/?cat=0&query=', 'showFilms')
CAT_SERIES = (URL_MAIN + 'search/?cat=0&query=', 'showSeries')

URL_SEARCH = (URL_MAIN + 'search/?cat=4&query=', 'showSearch')
URL_SEARCH_MOVIES = (URL_MAIN + 'search/?cat=0&query=', 'showSearch')
URL_SEARCH_SERIES = (URL_MAIN + 'search/?cat=0&query=', 'showSearch')
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
        sUrl = URL_MAIN + 'search/?cat=0&query=' + urllib.parse.quote(sSearchText)
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    __showTorrents(sHtmlContent)

def showFilms():
    __showSearchPrompt('search/?cat=0&query=')

def showSeries():
    __showSearchPrompt('search/?cat=0&query=')

def __showSearchPrompt(sSearchBase):
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    if sUrl.endswith('query='):
        oGui = cGui()
        sSearchText = oGui.showKeyBoard()
        if not sSearchText:
            oGui.setEndOfDirectory()
            return
        sUrl = sUrl + urllib.parse.quote(sSearchText)
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    __showTorrents(sHtmlContent)

def __showTorrents(sHtmlContent):
    oGui = cGui()
    oParser = cParser()

    sHtmlContent = re.sub(r'\r?\n', '', sHtmlContent)
    sPattern = r'<a href="(https?://[^"]*/torrent/\d+[^"]*)" class="detLink"[^>]*>([^<]+)</a>.*?<td align="right">(\d+)</td>.*?<td align="right">(\d+)</td>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sUrl = aEntry[0]
            sTitle = html.unescape(aEntry[1].strip()).replace('&#039;', "'").replace('&amp;', '&').replace('&quot;', '"')
            sSeeds = aEntry[2].strip()
            sLeechers = aEntry[3].strip()
            sDisplayName = '{}\n[COLOR grey]Seeds: {} | Leechers: {}[/COLOR]'.format(sTitle, sSeeds, sLeechers)

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
    sPattern = r'href="([^"]+)" rel="next"'
    oParser = cParser()
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
