import re

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import VSlog, siteManager, addon

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')

SITE_IDENTIFIER = 'annuaire_telechargement'
SITE_NAME = 'Annuaire Telechargement'
SITE_DESC = 'French DDL site'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

CAT_FILMS = (URL_MAIN + '/film/vf/', 'showFilms')
CAT_SERIES = (URL_MAIN + '/serie/', 'showSeries')

URL_SEARCH = (URL_MAIN, 'showSearch')
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
        oRequestHandler = cRequestHandler(URL_MAIN)
        oRequestHandler.setRequestType(1)
        oRequestHandler.addParameters('do', 'search')
        oRequestHandler.addParameters('subaction', 'search')
        oRequestHandler.addParameters('story', sSearchText)
        sHtmlContent = oRequestHandler.request()
        __showTorrents(sHtmlContent)
        oGui.setEndOfDirectory()

def showFilms():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    __showTorrents(sHtmlContent, sUrl)
    oGui.setEndOfDirectory()

def showSeries():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    __showTorrents(sHtmlContent, sUrl)
    oGui.setEndOfDirectory()

def __showTorrents(sHtmlContent, sCurrentUrl=''):
    oGui = cGui()
    oParser = cParser()

    sPattern = r'<a class="short-poster[^"]*"[^>]*href="(/(?:film|serie)/\d+[^"]*)"[^>]*>.*?<img src="([^"]+)"[^>]*>.*?<div class="short-title">([^<]+)</div>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sUrl = aEntry[0]
            sThumb = URL_MAIN + aEntry[1]
            sTitle = aEntry[2].strip()

            oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + sUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, '', oOutputParameterHandler)

    sNextPage = __checkForNextPage(sHtmlContent, sCurrentUrl)
    if sNextPage:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sNextPage)
        oGui.addDir(SITE_IDENTIFIER, 'showFilms', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def __checkForNextPage(sHtmlContent, sCurrentUrl):
    if not sCurrentUrl:
        return False

    # Extract current page number from URL
    oParser = cParser()
    sPagePattern = r'/page/(\d+)/'
    aPageMatch = oParser.parse(sCurrentUrl, sPagePattern)
    if aPageMatch[0]:
        iCurrentPage = int(aPageMatch[1][0])
        iNextPage = iCurrentPage + 1
        sNextUrl = sCurrentUrl.replace(f'/page/{iCurrentPage}/', f'/page/{iNextPage}/')
    else:
        sNextUrl = sCurrentUrl.rstrip('/') + '/page/2/'
        iNextPage = 2

    # Check if the next page link exists in the HTML
    sCheckPattern = rf'href="[^"]*/page/{iNextPage}/"'
    aCheckResult = oParser.parse(sHtmlContent, sCheckPattern)
    if aCheckResult[0]:
        return sNextUrl

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

    if not sThumb:
        sThumbPattern = r'<img[^>]*src="(/poster/[^"]+)"'
        aThumb = oParser.parse(sHtmlContent, sThumbPattern)
        if aThumb[0]:
            sThumb = URL_MAIN + aThumb[1][0]

    hosterAdded = False
    streamUrls = []

    sPlayerPattern = r'<div class="player-option[^"]*"[^>]*data-url-default="([^"]+)"'
    aPlayers = oParser.parse(sHtmlContent, sPlayerPattern)
    if aPlayers[0]:
        for streamUrl in aPlayers[1]:
            if streamUrl not in streamUrls:
                streamUrls.append(streamUrl)

    sVersionPattern = r'<div class="version-option"[^>]*data-url="([^"]+)"'
    aVersions = oParser.parse(sHtmlContent, sVersionPattern)
    if aVersions[0]:
        for streamUrl in aVersions[1]:
            if streamUrl not in streamUrls:
                streamUrls.append(streamUrl)

    for streamUrl in streamUrls:
        sTitle = sMovieTitle + ' [COLOR violet]Stream[/COLOR]'

        oHoster = cHosterGui().checkHoster(streamUrl)
        if oHoster:
            oHoster.setDisplayName(sTitle)
            oHoster.setFileName(sMovieTitle)
            cHosterGui().showHoster(oGui, oHoster, streamUrl, sThumb)
            hosterAdded = True

    if not hosterAdded:
        sIframePattern = r'<iframe[^>]*src="([^"]+)"'
        aIframes = oParser.parse(sHtmlContent, sIframePattern)
        if aIframes[0]:
            for streamUrl in aIframes[1]:
                if streamUrl and not streamUrl.startswith('javascript'):
                    sTitle2 = sMovieTitle + ' [COLOR orange]Stream[/COLOR]'
                    oHoster2 = cHosterGui().checkHoster(streamUrl)
                    if oHoster2:
                        oHoster2.setDisplayName(sTitle2)
                        oHoster2.setFileName(sMovieTitle)
                        cHosterGui().showHoster(oGui, oHoster2, streamUrl, sThumb)
                        hosterAdded = True

    if not hosterAdded:
        sDlPattern = r'href="(https://dl-protect\.link/[^"]+)"'
        aDl = oParser.parse(sHtmlContent, sDlPattern)
        if aDl[0]:
            for dlUrl in aDl[1]:
                sTitle3 = sMovieTitle + ' [COLOR orange]DDL[/COLOR]'
                oHoster3 = cHosterGui().checkHoster(dlUrl)
                if oHoster3:
                    oHoster3.setDisplayName(sTitle3)
                    oHoster3.setFileName(sMovieTitle)
                    cHosterGui().showHoster(oGui, oHoster3, dlUrl, sThumb)
                    hosterAdded = True

    oGui.setEndOfDirectory()
