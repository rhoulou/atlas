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

SITE_IDENTIFIER = 'zone_telechargement_estate'
SITE_NAME = 'Zone Telechargement (.estate)'
SITE_DESC = 'French DDL site'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

FILM_CATEGORIES = [
    ('Tous les Films', URL_MAIN + '/?p=films'),
    ('Exclus (Films populaires)', URL_MAIN + '/?p=films&s=exclus'),
    ('Blu-Ray 1080p/720p', URL_MAIN + '/?p=films&s=blu-ray_1080p-720p'),
    ('ULTRA HD 4K', URL_MAIN + '/?p=films&s=ultra-hd-4k'),
    ('Dessins animés', URL_MAIN + '/?p=films&s=dessins_animes'),
    ('DVDRIP/BDRIP', URL_MAIN + '/?p=films&s=dvdrip-dbrip'),
    ('DVDRIP HQ', URL_MAIN + '/?p=films&s=dvdrip-hq'),
    ('DVDSCR/R5/TS/CAM', URL_MAIN + '/?p=films&s=dvdsrc-r5-ts-cam'),
    ('Films VOSTFR', URL_MAIN + '/?p=films&s=film-vostfr'),
    ('Films VO', URL_MAIN + '/?p=films&s=_film-vo'),
    ('Vieux Films', URL_MAIN + '/?p=films&s=vieux-films'),
]

SERIES_CATEGORIES = [
    ('Toutes les Series', URL_MAIN + '/?p=series'),
    ('Series VF', URL_MAIN + '/?p=series&s=vf'),
    ('Series VF HD', URL_MAIN + '/?p=series&s=vf-hq'),
    ('Series VOSTFR', URL_MAIN + '/?p=series&s=vostfr'),
    ('Series VOSTFR HD', URL_MAIN + '/?p=series&s=vostfr-hq'),
    ('Series MULTI 4K UHD', URL_MAIN + '/?p=series&s=multi-4k'),
]

URL_SEARCH = (URL_MAIN, 'showSearch')
FUNCTION_SEARCH = 'showSearch'


def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search', icons + '/Search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/?p=films')
    oGui.addDir(SITE_IDENTIFIER, 'showFilmsCat', 'Films', icons + '/Movies.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/?p=series')
    oGui.addDir(SITE_IDENTIFIER, 'showSeriesCat', 'Series', icons + '/TVShows.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showFilmsCat():
    oGui = cGui()
    for sLabel, sUrl in FILM_CATEGORIES:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oGui.addDir(SITE_IDENTIFIER, 'showFilms', sLabel, icons + '/Movies.png', oOutputParameterHandler)
    oGui.setEndOfDirectory()


def showSeriesCat():
    oGui = cGui()
    for sLabel, sUrl in SERIES_CATEGORIES:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oGui.addDir(SITE_IDENTIFIER, 'showSeries', sLabel, icons + '/TVShows.png', oOutputParameterHandler)
    oGui.setEndOfDirectory()


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sSearchUrl = URL_MAIN + '/?p=films&search=' + urllib.parse.quote(sSearchText)
        oRequestHandler = cRequestHandler(sSearchUrl)
        sHtmlContent = oRequestHandler.request()
        __showContent(sHtmlContent)
        oGui.setEndOfDirectory()


def showFilms():
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    __showContent(sHtmlContent, sUrl)


def showSeries():
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    __showContent(sHtmlContent, sUrl)


def __showContent(sHtmlContent, sCurrentUrl=''):
    oGui = cGui()

    aResult = __parseListing(sHtmlContent)

    if aResult:
        for sIdPath, sThumb, sTitle, sQualite, sLangue in aResult:
            sQualif = f'{sQualite} ({sLangue})'
            sDisplayName = sTitle + ' [COLOR violet]' + sQualif + '[/COLOR]'

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/?p=film&id=' + sIdPath)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sDisplayName, '', sThumb, '', oOutputParameterHandler)

    sNextPage = __checkForNextPage(sHtmlContent, sCurrentUrl)
    if sNextPage:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sNextPage)
        sFunc = 'showFilms' if 'film' in sCurrentUrl else 'showSeries'
        oGui.addDir(SITE_IDENTIFIER, sFunc, '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def __parseListing(sHtmlContent):
    oParser = cParser()

    sBlockPattern = r'cover_global(.+?)(?=cover_global|\Z)'
    sItemPattern = (
        r'href="\?p=(?:film|serie)&id=(\d+[^"]+)".*?'
        r'src="(/img/films/[^"]+)".*?'
        r'cover_infos_title">.*?<a[^>]*>([^<]+)</a>.*?'
        r'<b>([^<]+)</b>.*?'
        r'<b>\((.+?)\)</b>'
    )

    aBlocks = oParser.parse(sHtmlContent, sBlockPattern)
    if not aBlocks[0]:
        return []

    aResult = []
    for block in aBlocks[1]:
        aItem = oParser.parse(block, sItemPattern)
        if aItem[0]:
            aResult.append(aItem[1][0])

    return aResult


def __checkForNextPage(sHtmlContent, sCurrentUrl):
    if not sCurrentUrl:
        return False

    sPattern = r'href="([^"]+)"[^>]*>Suivant'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        sNextPath = aResult[1][0]
        if sNextPath.startswith('/'):
            return URL_MAIN.rstrip('/') + sNextPath
        return URL_MAIN + sNextPath

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
        sThumbPattern = r'<img src="(/img/films/[^"]+)"'
        aThumb = oParser.parse(sHtmlContent, sThumbPattern)
        if aThumb[0]:
            sThumb = URL_MAIN + aThumb[1][0]

    sDescPattern = r'<meta name="description" content="([^"]+)"'
    aDesc = oParser.parse(sHtmlContent, sDescPattern)
    if aDesc[0]:
        sInfo = aDesc[1][0]
        oGui.addText(SITE_IDENTIFIER, '[COLOR skyblue]' + sInfo + '[/COLOR]')

    sSynopsisPattern = r'synopsis\.png.*?<em>([^<]+)'
    aSynopsis = oParser.parse(sHtmlContent, sSynopsisPattern)
    if aSynopsis[0]:
        sSynopsis = aSynopsis[1][0].strip()
        if sSynopsis:
            oGui.addText(SITE_IDENTIFIER, '[COLOR white]' + sSynopsis + '[/COLOR]')

    hosterAdded = False

    sHosterPattern = r'<b><div[^>]*>([^<]+)</div></b><b><a[^>]*href="(https://dl-protect\.link/[^"]+)"[^>]*>'
    aHosters = oParser.parse(sHtmlContent, sHosterPattern)
    if aHosters[0]:
        for sHoster, dlUrl in aHosters[1]:
            sLabel = f'{sHoster} [COLOR orange]DDL[/COLOR]'
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('dlUrl', dlUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oGui.addDir(SITE_IDENTIFIER, 'dlResolve', sLabel, icons + '/Sources.png', oOutputParameterHandler)
            hosterAdded = True

    sPremiumPattern = r'href="(https://dl-protect\.link/rqts-url[^"]+)"[^>]*>.*?PREMIUM'
    aPremium = oParser.parse(sHtmlContent, sPremiumPattern)
    if aPremium[0]:
        dlUrl = aPremium[1][0]
        sLabel = 'Premium [COLOR gold]PREMIUM[/COLOR]'
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('dlUrl', dlUrl)
        oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle)
        oOutputParameterHandler.addParameter('sThumb', sThumb)
        oGui.addDir(SITE_IDENTIFIER, 'dlResolve', sLabel, icons + '/Sources.png', oOutputParameterHandler)
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

    sOtherVerPattern = (
        r'<a href="\?p=film&id=(\d+[^"]+)"[^>]*>.*?'
        r'<span class="otherquality">.*?'
        r'<b>([^<]+)</b>.*?'
        r'<b>\((.+?)\)</b>'
    )
    aOtherVer = oParser.parse(sHtmlContent, sOtherVerPattern)
    if aOtherVer[0]:
        for aEntry in aOtherVer[1]:
            sVerId = aEntry[0]
            sQualite = aEntry[1].strip()
            sLangue = aEntry[2].strip()
            sLabel = sMovieTitle + ' [COLOR orange]' + sQualite + ' (' + sLangue + ')[/COLOR]'

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/?p=film&id=' + sVerId)
            oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle + ' [' + sQualite + ' (' + sLangue + ')]')
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            oGui.addDir(SITE_IDENTIFIER, 'showHosters', sLabel, icons + '/Movies.png', oOutputParameterHandler)
            hosterAdded = True

    if not hosterAdded:
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]No links found[/COLOR]')

    oGui.setEndOfDirectory()


def dlResolve():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    dlUrl = oInputParameterHandler.getValue('dlUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    hosterAdded = False

    try:
        oReq = cRequestHandler(dlUrl)
        oReq.request()
        sRealUrl = oReq.getRealUrl()
    except:
        sRealUrl = dlUrl

    if sRealUrl and sRealUrl != dlUrl:
        oHoster = cHosterGui().checkHoster(sRealUrl)
        if oHoster:
            oHoster.setDisplayName(sMovieTitle)
            oHoster.setFileName(sMovieTitle)
            cHosterGui().showHoster(oGui, oHoster, sRealUrl, sThumb)
            hosterAdded = True

    if not hosterAdded:
        from resources.lib.comaddon import VSlog
        VSlog('DDL link (open in browser): ' + dlUrl)
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]DDL link — open in browser[/COLOR]')

    oGui.setEndOfDirectory()
