# -*- coding: utf-8 -*-
# shortseris.online - Kodi plugin

import re
import urllib.request
import urllib.parse

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.comaddon import VSlog, siteManager, addon
from resources.lib.parser import cParser

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/sites/logos/shortseris_online.png'

SITE_IDENTIFIER = 'shortseris_online'
SITE_NAME = 'ShortSeris'
SITE_DESC = 'arabic vod'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

SERIES_ALL = (URL_MAIN + 'index.php', 'showSeries')
FUNCTION_SEARCH = 'showSeries'
URL_SEARCH_SERIES = (URL_MAIN + 'search.php?q=', 'showSeries')


def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'بحث', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIES_ALL[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'كل المسلسلات', icons + '/Series.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = URL_MAIN + 'search.php?q=' + urllib.parse.quote(sSearchText)
        showSeries(sUrl)
        oGui.setEndOfDirectory()
        return


def _fetch(url):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        resp = urllib.request.urlopen(req, timeout=15)
        return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        VSlog('shortseris_online _fetch error: %s %s' % (url, str(e)))
        return ''


def _fixUrl(path):
    if not path:
        return ''
    if ' ' in path or re.search(r'[\u0600-\u06FF\u0750-\u077F]', path):
        full = path if path.startswith('http') else URL_MAIN + path
        parts = urllib.parse.urlsplit(full)
        path_encoded = urllib.parse.quote(parts.path, safe='/:@!$&\'()*+,;=')
        query_encoded = urllib.parse.quote(parts.query, safe='=&%+')
        return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path_encoded, query_encoded, parts.fragment))
    if path.startswith('http'):
        return path
    if path.startswith('/'):
        return URL_MAIN.rstrip('/') + path
    return URL_MAIN + path


def showSeries(sSearch=''):
    oGui = cGui()
    if sSearch:
        sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    sHtmlContent = _fetch(sUrl).replace('\n', ' ').replace('\r', ' ')

    bIsSearch = 'search.php' in sUrl
    bFound = False

    if bIsSearch:
        sPattern = r'<a\s+class="search-result-card"\s+href="([^"]*)"[^>]*>.*?<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)".*?<span\s+class="result-type\s+(\w+)">'
        oParser = cParser()
        aResult = oParser.parse(sHtmlContent, sPattern)
        if aResult[0]:
            bFound = True
            oOutputParameterHandler = cOutputParameterHandler()
            for aEntry in aResult[1]:
                sUrl2 = _fixUrl(aEntry[0])
                sThumb = _fixUrl(aEntry[1])
                sTitle = aEntry[2].strip()
                sType = aEntry[3].strip()

                oOutputParameterHandler.addParameter('siteUrl', sUrl2)
                oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
                oOutputParameterHandler.addParameter('sThumbnail', sThumb)

                if sType == 'series':
                    oGui.addTV(SITE_IDENTIFIER, 'showEpisodes', sTitle, '', sThumb, '', oOutputParameterHandler)
                else:
                    oGui.addEpisode(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, '', oOutputParameterHandler)
    else:
        sPattern = r'<a\s+class="series-card-pro"[^>]*href="([^"]*)"[^>]*>.*?<img[^>]*class="series-poster-pro"[^>]*src="([^"]*)"[^>]*alt="([^"]*)".*?<span class="episode-count-pill">([^<]*)</span>.*?<h3>([^<]*)</h3>'
        oParser = cParser()
        aResult = oParser.parse(sHtmlContent, sPattern)
        if aResult[0]:
            bFound = True
            oOutputParameterHandler = cOutputParameterHandler()
            for aEntry in aResult[1]:
                sUrl2 = _fixUrl(aEntry[0])
                sThumb = _fixUrl(aEntry[1])
                sTitle = aEntry[4].strip()
                sInfo = aEntry[3].strip()

                oOutputParameterHandler.addParameter('siteUrl', sUrl2)
                oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
                oOutputParameterHandler.addParameter('sThumbnail', sThumb)

                oGui.addTV(SITE_IDENTIFIER, 'showEpisodes', sTitle, '', sThumb, sInfo, oOutputParameterHandler)

    if bFound and not bIsSearch:
        sNextPage = __checkForNextPage(sHtmlContent)
        if sNextPage:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showSeries', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    if not sSearch:
        oGui.setEndOfDirectory()


def __checkForNextPage(sHtmlContent):
    sHtmlContent = sHtmlContent.replace('\n', ' ').replace('\r', ' ')
    oParser = cParser()
    sPattern = r'<a\s+href="(index\.php\?page=\d+)"[^>]*>\s*التالي'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        return URL_MAIN + aResult[1][0]

    sPattern = r'<a\s+href="(index\.php\?page=\d+#series)"[^>]*>\s*التالي'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        return URL_MAIN + aResult[1][0]

    return False


def showEpisodes():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = _fixUrl(oInputParameterHandler.getValue('siteUrl'))
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumbnail = oInputParameterHandler.getValue('sThumbnail')

    sHtmlContent = _fetch(sUrl).replace('\n', ' ').replace('\r', ' ')

    sPattern = r'<a\s+class="episode episode-rich"[^>]*href="([^"]*)"[^>]*>.*?<span class="episode-number-badge">([^<]*)</span>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sUrl2 = _fixUrl(aEntry[0])
            sEpisode = aEntry[1].strip()
            sTitle = sMovieTitle + ' - ' + sEpisode

            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumbnail', sThumbnail)
            oGui.addEpisode(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumbnail, '', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = _fixUrl(oInputParameterHandler.getValue('siteUrl'))
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumbnail = oInputParameterHandler.getValue('sThumbnail')

    sHtmlContent = _fetch(sUrl).replace('\n', ' ').replace('\r', ' ')

    sPattern = r'data-slide-index="(\d+)"[^>]*data-episode-index="\d+"[^>]*data-url="([^"]*)"[^>]*>.*?data-src="(stream[^"]*)"'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        for aEntry in aResult[1]:
            iSlide = int(aEntry[0])
            sEpisodeUrl = aEntry[1].replace('&amp;', '&')
            sStreamUrl = aEntry[2]

            sHosterUrl = _fixUrl(sStreamUrl)
            if 'Referer' not in sHosterUrl:
                sHosterUrl = sHosterUrl + '|Referer=' + URL_MAIN

            oHoster = cHosterGui().getHoster('lien_direct')
            if oHoster:
                sDisplayTitle = sMovieTitle + ' - الحلقة %d' % (iSlide + 1)
                oHoster.setDisplayName(sDisplayTitle)
                oHoster.setFileName(sMovieTitle)
                cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumbnail)

    oGui.setEndOfDirectory()
