import re
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

SITE_IDENTIFIER = 'sharework4'
SITE_NAME = 'Sharework'
SITE_DESC = 'French torrent site'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

CAT_FILMS = (URL_MAIN + '/category/films', 'showFilms')
CAT_SERIES = (URL_MAIN + '/category/series', 'showSeries')

URL_SEARCH = (URL_MAIN + '/recherche/', 'showSearch')
FUNCTION_SEARCH = 'showSearch'

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

def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = URL_MAIN + '/recherche/' + sSearchText
        __showTorrents(sUrl)
        oGui.setEndOfDirectory()

def showFilms():
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    __showTorrents(sUrl)

def showSeries():
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    __showTorrents(sUrl)

def __showTorrents(sUrl):
    oGui = cGui()
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    oParser = cParser()

    sPattern = r'<a href="/detail/(\d+)"[^>]*>[^<]*<span[^>]*><img src=\'([^\']+)\'[^>]*>.*?<div class="maxis">([^<]+)</div>.*?</span></a></div></td><td class="liste-accueil-taille"[^>]*>([^<]+)</td><td class="sources[^"]*"[^>]*>([^<]+)</td><td class="clients[^"]*"[^>]*>([^<]+)</td>'

    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sDetailId = aEntry[0]
            sThumb = aEntry[1]
            sTitle = aEntry[2].strip()
            sSize = aEntry[3].strip()
            sSeeds = aEntry[4].strip()
            sLeech = aEntry[5].strip()
            sDesc = 'Size: {} | Seeds: {} | Leech: {}'.format(sSize, sSeeds, sLeech)

            oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/detail/' + sDetailId)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('sDesc', sDesc)

            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

    sNextPage = __checkForNextPage(sHtmlContent)
    if sNextPage:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sNextPage)
        oGui.addDir(SITE_IDENTIFIER, 'showFilms', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def __checkForNextPage(sHtmlContent):
    sPattern = r'<li><a href="(/category/[^"]+/[^"]+)"[^>]*>Suivant'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        return URL_MAIN + aResult[1][0]
    return False

def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    oParser = cParser()

    sPattern = r'href="(magnet:[^"]+)"'
    aResult = oParser.parse(sHtmlContent, sPattern)

    magnetAdded = False
    if aResult[0]:
        for magnetUrl in aResult[1]:
            encoded = urllib.parse.quote(magnetUrl, safe='')
            elementumUrl = 'plugin://plugin.video.elementum/play?uri=' + encoded
            sTitle = sMovieTitle + ' [COLOR violet]Magnet[/COLOR]'

            oHoster = cHosterGui().getHoster('elementum')
            oHoster.setDisplayName(sTitle)
            oHoster.setFileName(sMovieTitle)
            cHosterGui().showHoster(oGui, oHoster, elementumUrl, sThumb)
            magnetAdded = True

    if not magnetAdded:
        sPattern2 = r'href="(/direct/(\d+))"'
        aResult2 = oParser.parse(sHtmlContent, sPattern2)
        if aResult2[0]:
            for directUrl in aResult2[1]:
                fullUrl = URL_MAIN.rstrip('/') + directUrl[0]
                sTitle2 = sMovieTitle + ' [COLOR orange]Direct[/COLOR]'
                oHoster2 = cHosterGui().checkHoster(fullUrl)
                if oHoster2:
                    oHoster2.setDisplayName(sTitle2)
                    oHoster2.setFileName(sMovieTitle)
                    cHosterGui().showHoster(oGui, oHoster2, fullUrl, sThumb)

    oGui.setEndOfDirectory()
