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

SITE_IDENTIFIER = 'cpasbien'
SITE_NAME = 'Cpasbien'
SITE_DESC = 'French torrent site'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

CAT_FILMS = (URL_MAIN + '/category/films', 'showFilms')
CAT_SERIES = (URL_MAIN + '/category/series', 'showSeries')

URL_SEARCH = (URL_MAIN, 'showSearch')
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
    sSearchText = urllib.parse.unquote(sSearchText)
    oRequestHandler = cRequestHandler(URL_MAIN)
    oRequestHandler.setRequestType(1)
    oRequestHandler.addParameters('torrentSearch', sSearchText)
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

    sThumbPattern = r'href="/detail/(\d+)"[^>]*><img[^>]*src="([^"]+)"[^>]*title="([^"]+)"'
    aThumbs = oParser.parse(sHtmlContent, sThumbPattern)
    dThumbs = {}
    if aThumbs[0]:
        for entry in aThumbs[1]:
            dThumbs[entry[0]] = entry[1]

    sPattern = r'<a href="/detail/(\d+)" title="([^"]*)" class="titre">.*?<div class="maxi">([^<]+)</div></a>.*?<div class="poid">([^<]+)</div>.*?<span class="seed_ok">(\d+)'

    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sDetailId = aEntry[0]
            sTitle = aEntry[2].strip()
            sSize = aEntry[3].strip()
            sSeeds = aEntry[4].strip()
            sThumb = dThumbs.get(sDetailId, '')
            sDisplayName = '{} [{}] [COLOR lime]S:{}[/COLOR]'.format(sTitle, sSize, sSeeds)

            oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/detail/' + sDetailId)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)

            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sDisplayName, icons + '/Movies.png', sThumb, sDisplayName, oOutputParameterHandler)

    sNextPage = __checkForNextPage(sHtmlContent)
    if sNextPage:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sNextPage)
        oGui.addDir(SITE_IDENTIFIER, 'showFilms', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def __checkForNextPage(sHtmlContent):
    sPattern = r'href="(/category/[^"]*/\d+)"[^>]*>Suivant'
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

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    oParser = cParser()

    sPattern = r'src="(https://zimage[^"]+)"'
    aThumb = oParser.parse(sHtmlContent, sPattern)
    sThumb = aThumb[1][0] if aThumb[0] else ''

    sPattern = r'href="(/get_torrents/[^"]+)"'
    aResult = oParser.parse(sHtmlContent, sPattern)

    downloadAdded = False
    if aResult[0]:
        for torrentPath in aResult[1]:
            torrentUrl = URL_MAIN.rstrip('/') + torrentPath
            encoded = urllib.parse.quote(torrentUrl, safe='')
            elementumUrl = 'plugin://plugin.video.elementum/play?uri=' + encoded
            sTitle = sMovieTitle + ' [COLOR violet]Torrent[/COLOR]'

            oHoster = cHosterGui().getHoster('elementum')
            oHoster.setDisplayName(sTitle)
            oHoster.setFileName(sMovieTitle)
            cHosterGui().showHoster(oGui, oHoster, elementumUrl, sThumb)
            downloadAdded = True

    if not downloadAdded:
        sPattern2 = r'href="(/get_torrents/[^"]+)"'
        aResult2 = oParser.parse(sHtmlContent, sPattern2)
        if aResult2[0]:
            for torrentPath in aResult2[1]:
                fullUrl = URL_MAIN.rstrip('/') + torrentPath
                sTitle2 = sMovieTitle + ' [COLOR orange]Torrent[/COLOR]'
                oHoster2 = cHosterGui().checkHoster(fullUrl)
                if oHoster2:
                    oHoster2.setDisplayName(sTitle2)
                    oHoster2.setFileName(sMovieTitle)
                    cHosterGui().showHoster(oGui, oHoster2, fullUrl, sThumb)

    oGui.setEndOfDirectory()
