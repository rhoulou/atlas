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

SITE_IDENTIFIER = 'annuaire_telechargement_estate'
SITE_NAME = 'Annuaire Telechargement (.estate)'
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
    oParser = cParser()

    sPattern = (
        r'<a href="/\?p=(film|serie)&id=([^"]+)"[^>]*>'
        r'.*?<img class="affiche" src="(/[^"]+)"[^>]*>'
        r'.*?<div class="titref">([^<]+)</div>'
        r'.*?<div class="qualif">([^<]+)</div>'
    )

    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        for aEntry in aResult[1]:
            sType = aEntry[0]
            sIdPath = aEntry[1]
            sThumb = URL_MAIN + aEntry[2]
            sTitle = aEntry[3].strip()
            sQualif = aEntry[4].strip()

            sDisplayName = sTitle + ' [COLOR violet]' + sQualif + '[/COLOR]'

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/?p=' + sType + '&id=' + sIdPath)
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


def __checkForNextPage(sHtmlContent, sCurrentUrl):
    if not sCurrentUrl:
        return False

    sPattern = r'<a class="page-link" href="([^"]+)"[^>]*rel="next"'
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
        sThumbPattern = r'<img class="affiche"[^>]*src="(/[^"]+)"'
        aThumb = oParser.parse(sHtmlContent, sThumbPattern)
        if aThumb[0]:
            sThumb = URL_MAIN + aThumb[1][0]

    hosterAdded = False

    sHosterPattern = r'href="(https://dl-protect\.link/[^"]+)"[^>]*>.*?class="providers[^"]*"[^>]*title="([^"]+)".*?class="fichetaille">([^<]+)<'
    aHosters = oParser.parse(sHtmlContent, sHosterPattern)
    if aHosters[0]:
        for dlUrl, sHoster, sSize in aHosters[1]:
            sLabel = f'{sHoster} ({sSize}) [COLOR orange]DDL[/COLOR]'
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('dlUrl', dlUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oGui.addDir(SITE_IDENTIFIER, 'dlResolve', sLabel, icons + '/Sources.png', oOutputParameterHandler)
            hosterAdded = True

    sPremiumPattern = r'href="(https://dl-protect\.link/rqts-url[^"]+)"[^>]*>.*?<b>([^<]+)</b>.*?class="fichetaille">([^<]+)<'
    aPremium = oParser.parse(sHtmlContent, sPremiumPattern)
    if aPremium[0]:
        for dlUrl, sLabel, sSize in aPremium[1]:
            sLabel = f'{sLabel.strip()} ({sSize}) [COLOR gold]PREMIUM[/COLOR]'
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
