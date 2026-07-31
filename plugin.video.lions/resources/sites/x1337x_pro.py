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

SITE_IDENTIFIER = 'x1337x_pro'
SITE_NAME = '1337x'
SITE_DESC = '1337x torrent site'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

CAT_FILMS = URL_MAIN + '/cat/movies/'
CAT_SERIES = URL_MAIN + '/cat/tv/'
CAT_XXX = URL_MAIN + '/cat/xxx/'

FUNCTION_SEARCH = 'showSearch'
URL_SEARCH_DRAMAS = ('', 'showSearch')

def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search', icons + '/Search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', CAT_FILMS)
    oGui.addDir(SITE_IDENTIFIER, 'showFilms', 'Films', icons + '/Movies.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', CAT_SERIES)
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'Series', icons + '/TVShows.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', CAT_XXX)
    oGui.addDir(SITE_IDENTIFIER, 'showXXX', 'XXX', icons + '/Movies.png', oOutputParameterHandler)

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
        sUrl = URL_MAIN + '/search/?q=' + urllib.parse.quote(sSearchText)
        oRequestHandler = cRequestHandler(sUrl)
        sHtmlContent = oRequestHandler.request()
        __showTorrents(sHtmlContent, sUrl)

def showFilms():
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    __showTorrents(sHtmlContent, sUrl, 'movies')

def showSeries():
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    __showTorrents(sHtmlContent, sUrl, 'tv')

def showXXX():
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    __showTorrents(sHtmlContent, sUrl, 'xxx')

def __showTorrents(sHtmlContent, sUrl, sCatName=''):
    oGui = cGui()
    oParser = cParser()

    sPattern = r'<tr[^>]*>.*?<td class="coll-1 name"[^>]*>.*?<a[^>]*?href="([^"]+)"[^>]*?class="openAdd"[^>]*>([^<]+)</a>.*?<td class="coll-2 seeds"[^>]*>(\d+)</td>.*?<td class="coll-3 leeches"[^>]*>(\d+)</td>.*?<td class="coll-4 size[^"]*"[^>]*>([^<]+)</td>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sUrlTorrent = aEntry[0]
            sTitle = html.unescape(aEntry[1].strip()).replace('&#039;', "'").replace('&amp;', '&').replace('&quot;', '"')
            sSeeds = aEntry[2].strip()
            sLeech = aEntry[3].strip()
            sSize = aEntry[4].strip()
            sDisplayName = '{}\n[COLOR grey]Size: {} | S:{} L:{}[/COLOR]'.format(sTitle, sSize, sSeeds, sLeech)

            if sUrlTorrent.startswith('http'):
                oOutputParameterHandler.addParameter('siteUrl', sUrlTorrent)
            else:
                oOutputParameterHandler.addParameter('siteUrl', URL_MAIN.rstrip('/') + sUrlTorrent)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)

            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sDisplayName, icons + '/Movies.png', '', sDisplayName, oOutputParameterHandler)

    sNextPage = __checkForNextPage(sHtmlContent, sUrl, sCatName)
    if sNextPage:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sNextPage)
        oGui.addDir(SITE_IDENTIFIER, 'showFilms', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def __checkForNextPage(sHtmlContent, sUrl, sCatName=''):
    if not sUrl:
        return False

    if '/search/' in sUrl:
        sPattern = r"<a[^>]*href='([^']+)'[^>]*>\s*Next\s*<"
        oParser = cParser()
        aResult = oParser.parse(sHtmlContent, sPattern)
        if aResult[0]:
            return aResult[1][0]
        sPattern = r'<a[^>]*href="([^"]+)"[^>]*>\s*Next\s*<'
        aResult = oParser.parse(sHtmlContent, sPattern)
        if aResult[0]:
            return aResult[1][0]
        return False

    if '/ajax/' in sUrl:
        parsed = urllib.parse.urlparse(sUrl)
        page = int(re.search(r'page=(\d+)', parsed.query).group(1)) + 1
        new_query = re.sub(r'page=\d+', 'page=' + str(page), parsed.query)
        return urllib.parse.urlunparse(parsed._replace(query=new_query))

    if sCatName:
        return URL_MAIN + '/ajax/datacat.php?page=2&q=&catname=' + sCatName

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
