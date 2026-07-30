# -*- coding: utf-8 -*-
# zombi https://github.com/zombiB/zombi-addons/

import re

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.comaddon import siteManager, addon
from resources.lib.parser import cParser
from resources.lib.util import cUtil

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/sites/logos/arabsciences.png'

SITE_IDENTIFIER = 'arabsciences'
SITE_NAME = 'Arabsciences'
SITE_DESC = 'arabic vod'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

DOC_NEWS = ('https://arabsciences.com/category/animals-categories/', 'showMovies')
URL_SEARCH = ('https://arabsciences.com/?s=', 'showMovies')
URL_SEARCH_MOVIES = ('https://arabsciences.com/?s=', 'showMovies')
URL_SEARCH_MISC = ('https://arabsciences.com/?s=', 'showMovies')
FUNCTION_SEARCH = 'showMovies'

def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', DOC_NEWS[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام وثائقية', icons + '/Documentary.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showSearch():
    oGui = cGui()

    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = 'https://arabsciences.com/?s=' + sSearchText
        showMovies(sUrl)
        oGui.setEndOfDirectory()
        return

def showMovies(sSearch=''):
    oGui = cGui()

    if sSearch:
        sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    oParser = cParser()
    # Match article listing: link with aria-label, title, image, excerpt
    sPattern = '<a\s+aria-label="([^"]+)"\s+href="([^"]+)"\s+class="post-thumb">[\s\S]*?<img[^>]+src="([^"]+)"[\s\S]*?<h2\s+class="post-title"><a[^>]+>([^<]+)</a></h2>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        for aEntry in aResult[1]:
            if "مقال" in aEntry[0]:
                continue

            sTitle = cUtil().unescape(aEntry[0])
            sThumb = aEntry[2]
            siteUrl = aEntry[1]
            sDesc = cUtil().unescape(aEntry[3])

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', siteUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            oGui.addMisc(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

        sNextPage = __checkForNextPage(sHtmlContent)
        if sNextPage:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    if not sSearch:
        oGui.setEndOfDirectory()

def __checkForNextPage(sHtmlContent):
    oParser = cParser()
    # Look for <link rel="next" href="...">
    sPattern = '<link\s+rel="next"\s+href="([^"]+)"'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        return aResult[1][0]

    return False

def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    # Pattern 1: iframe with frameborder attribute
    sPattern = 'src=(.+?)\s+frameborder'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        for aEntry in aResult[1]:
            url = aEntry.replace('?rel=0', '').replace('"', '').replace("'", '')
            if url.startswith('//'):
                url = 'http:' + url
            oHoster = cHosterGui().getHoster('resolver')
            oHoster.setDisplayName(sMovieTitle)
            oHoster.setFileName(sMovieTitle)
            cHosterGui().showHoster(oGui, oHoster, url, sThumb)

    # Pattern 2: YouTube embed URLs
    sPattern = 'https?://(?:www\.)?youtube\.com/embed/([^"&?\s]+)'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        for aEntry in aResult[1]:
            url = 'https://www.youtube.com/embed/' + aEntry
            oHoster = cHosterGui().getHoster('resolver')
            oHoster.setDisplayName(sMovieTitle)
            oHoster.setFileName(sMovieTitle)
            cHosterGui().showHoster(oGui, oHoster, url, sThumb)

    # Pattern 3: iframe with src attribute
    sPattern = '<iframe\s+src="([^"]+)"\s+width='
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        for aEntry in aResult[1]:
            url = aEntry.replace('?rel=0', '')
            if url.startswith('//'):
                url = 'http:' + url
            oHoster = cHosterGui().getHoster('resolver')
            oHoster.setDisplayName(sMovieTitle)
            oHoster.setFileName(sMovieTitle)
            cHosterGui().showHoster(oGui, oHoster, url, sThumb)

    oGui.setEndOfDirectory()
