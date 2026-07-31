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
LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/limetorrents_asia.png'

SITE_IDENTIFIER = 'limetorrents_asia'
SITE_NAME = 'LimeTorrents'
SITE_DESC = 'LimeTorrents torrent site'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

CAT_FILMS = (URL_MAIN + '/browse-torrents/Movies', 'showFilms')
CAT_SERIES = (URL_MAIN + '/browse-torrents/TV', 'showSeries')
CAT_OTHERS = (URL_MAIN + '/browse-torrents/Other', 'showFiles')

URL_SEARCH_MOVIES = (URL_MAIN + '/search?catname=movies&q=', 'showSearch')
URL_SEARCH_SERIES = (URL_MAIN + '/search?catname=tv&q=', 'showSeriesSearch')
URL_SEARCH_ANIMS = (URL_MAIN + '/search?catname=anime&q=', 'showSearch')
URL_SEARCH_DRAMAS = (URL_MAIN + '/search?catname=movies&q=', 'showSearch')
URL_SEARCH_OTHER = (URL_MAIN + '/search?catname=other&q=', 'showOtherSearch')
URL_SEARCH_ALL = (URL_MAIN + '/search?q=', 'showAllSearch')
URL_SEARCH = URL_SEARCH_ALL
URL_SEARCH_MISC = URL_SEARCH_ALL
FUNCTION_SEARCH = 'showSearch'
FUNCTION_SEARCH_SERIES = 'showSeriesSearch'
FUNCTION_SEARCH_OTHER = 'showOtherSearch'
FUNCTION_SEARCH_ALL = 'showAllSearch'

def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search Movies', icons + '/Search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSeriesSearch', 'Search TV Shows', icons + '/Search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showOtherSearch', 'Search Other', icons + '/Search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showAllSearch', 'Search All', icons + '/Search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', CAT_FILMS[0])
    oGui.addDir(SITE_IDENTIFIER, 'showFilms', 'Movies', icons + '/Movies.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', CAT_SERIES[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'TV Shows', icons + '/TVShows.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', CAT_OTHERS[0])
    oGui.addDir(SITE_IDENTIFIER, 'showFiles', 'Other', icons + '/Misc.png', oOutputParameterHandler)

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
        sUrl = URL_SEARCH_MOVIES[0] + urllib.parse.quote(sSearchText)
    __fetchAndShow(sUrl, 'showSearch')

def showSeriesSearch(sSearchText=''):
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
        sUrl = URL_SEARCH_SERIES[0] + urllib.parse.quote(sSearchText)
    __fetchAndShow(sUrl, 'showSeriesSearch')
    oGui.setEndOfDirectory()

def showOtherSearch(sSearchText=''):
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
        sUrl = URL_SEARCH_OTHER[0] + urllib.parse.quote(sSearchText)
    __fetchAndShow(sUrl, 'showOtherSearch')
    oGui.setEndOfDirectory()

def showAllSearch(sSearchText=''):
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
        sUrl = URL_SEARCH_ALL[0] + urllib.parse.quote(sSearchText)
    __fetchAndShow(sUrl, 'showAllSearch')
    oGui.setEndOfDirectory()

def showFilms():
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    __fetchAndShow(sUrl, 'showFilms')

def showSeries():
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    __fetchAndShow(sUrl, 'showSeries')

def showFiles():
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    __fetchAndShow(sUrl, 'showFiles')

def __fetchAndShow(sUrl, sNextFunc):
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    __showTorrents(sHtmlContent, sNextFunc)

def __showTorrents(sHtmlContent, sNextFunc='showFilms'):
    oGui = cGui()
    oParser = cParser()

    sPattern = r'<td class="tdleft">.*?(?:<div class="tt-name">)?.*?<a href="(https://limetorrents\.asia/[^"]+)"[^>]*class="openPopup"[^>]*>([^<]+)</a>.*?<td class="tdnormal">[^<]*</td>.*?<td class="tdnormal">([^<]+)</td>.*?<td class="tdseed">(\d+)</td>.*?<td class="tdleech">(\d+)</td>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        for aEntry in aResult[1]:
            sUrl = aEntry[0]
            sTitle = html.unescape(aEntry[1].strip()).replace('&#039;', "'").replace('&amp;', '&').replace('&quot;', '"')
            sSize = aEntry[2].strip()
            sSeeds = aEntry[3].strip()
            sLeech = aEntry[4].strip()
            sDisplayName = '{}\n[COLOR grey]Size: {} | S:{} L:{}[/COLOR]'.format(sTitle, sSize, sSeeds, sLeech)

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)

            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sDisplayName, icons + '/Movies.png', '', sDisplayName, oOutputParameterHandler)

    sNextPage = __checkForNextPage(sHtmlContent, sNextFunc)
    if sNextPage:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sNextPage)
        oGui.addDir(SITE_IDENTIFIER, sNextFunc, '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def __checkForNextPage(sHtmlContent, sNextFunc='showFilms'):
    oParser = cParser()

    if sNextFunc in ('showSearch', 'showSeriesSearch', 'showOtherSearch', 'showAllSearch'):
        sPattern = r'<button[^>]*id="loadMorep"[^>]*data-page="(\d+)"'
        aResult = oParser.parse(sHtmlContent, sPattern)
        if aResult[0]:
            nextPage = int(aResult[1][0]) + 1
            sQPattern = r'<span class="querytext">([^<]+)</span>'
            aQResult = oParser.parse(sHtmlContent, sQPattern)
            sQuery = urllib.parse.quote(aQResult[1][0]) if aQResult[0] else ''
            return URL_MAIN + '/data.php?page=' + str(nextPage) + '&q=' + sQuery + '&orderby=&order='
        return False

    catMap = {
        'showFilms': 'Movies',
        'showSeries': 'TV',
        'showFiles': 'Other',
    }
    sCatName = catMap.get(sNextFunc, 'Movies')
    sPattern = r'<button[^>]*id="loadMorepCat"[^>]*data-page="(\d+)"'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        nextPage = int(aResult[1][0]) + 1
        return URL_MAIN + '/getdata.php?page=' + str(nextPage) + '&catname=' + sCatName
    return False

def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    oParser = cParser()

    magnetAdded = False

    sPattern = r'href="(magnet:[^"]+)"'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        for magnetUrl in aResult[1]:
            magnetUrl = html.unescape(magnetUrl)
            __addMagnet(oGui, sMovieTitle, magnetUrl)
            magnetAdded = True

    if not magnetAdded:
        sPattern = r'<div class="dltorrent download_magnet".*?<a href="([^"]+)"[^>]*title="Magnet"'
        aResult = oParser.parse(sHtmlContent, sPattern)

        if aResult[0]:
            for sStoreUrl in aResult[1]:
                oRequestHandler = cRequestHandler(sStoreUrl)
                sStoreHtml = oRequestHandler.request()

                sPattern = r'href="(magnet:[^"]+)"[^>]*>Magnet Download</a>'
                aMagnetResult = oParser.parse(sStoreHtml, sPattern)

                if aMagnetResult[0]:
                    for magnetUrl in aMagnetResult[1]:
                        magnetUrl = html.unescape(magnetUrl)
                        __addMagnet(oGui, sMovieTitle, magnetUrl)
                        magnetAdded = True

    if not magnetAdded:
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]No links found[/COLOR]')

    oGui.setEndOfDirectory()

def __addMagnet(oGui, sMovieTitle, magnetUrl):
    encoded = urllib.parse.quote(magnetUrl, safe='')
    elementumUrl = 'plugin://plugin.video.elementum/play?uri=' + encoded
    sTitle = sMovieTitle + ' [COLOR violet]Magnet[/COLOR]'

    oHoster = cHosterGui().getHoster('elementum')
    oHoster.setDisplayName(sTitle)
    oHoster.setFileName(sMovieTitle)
    cHosterGui().showHoster(oGui, oHoster, elementumUrl, '')
