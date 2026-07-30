# -*- coding: utf-8 -*-
import re
import urllib.parse

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.comaddon import VSlog, siteManager, addon
from resources.lib.parser import cParser
import resolveurl

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/shiid4u_co.png'

SITE_IDENTIFIER = 'shiid4u_co'
SITE_NAME = 'Shiid4u'
SITE_DESC = 'arabic vod'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER).rstrip('/')
FUNCTION_SEARCH = 'showMovies'

def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D8%AC%D9%86%D8%A8%D9%8A')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Movies[/COLOR] Foreign', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D9%87%D9%86%D8%AF%D9%8A')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Movies[/COLOR] Hindi', icons + '/Hindi.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D9%86%D9%85%D9%8A')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Movies[/COLOR] Anime', icons + '/Anime.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D8%B3%D9%8A%D9%88%D9%8A%D8%A9')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Movies[/COLOR] Asian', icons + '/Asian.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%AA%D8%B1%D9%83%D9%8A%D8%A9')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Movies[/COLOR] Turkish', icons + '/Turkish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%B9%D8%B1%D8%A8%D9%8A')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Movies[/COLOR] Arabic', icons + '/Arabic.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA-%D8%A7%D8%AC%D9%86%D8%A8%D9%8A')
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', '[COLOR gold]Series[/COLOR] Foreign', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA-%D8%A7%D9%86%D9%85%D9%8A')
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', '[COLOR gold]Series[/COLOR] Anime', icons + '/Anime.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA-%D8%AA%D8%B1%D9%83%D9%8A%D8%A9')
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', '[COLOR gold]Series[/COLOR] Turkish', icons + '/Turkish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA-%D8%A7%D8%B3%D9%8A%D9%88%D9%8A%D8%A9')
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', '[COLOR gold]Series[/COLOR] Asian', icons + '/Asian.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA-%D9%85%D8%AF%D8%A8%D9%84%D8%AC%D8%A9')
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', '[COLOR gold]Series[/COLOR] Dubbed', icons + '/Arabic.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA-%D8%B9%D8%B1%D8%A8%D9%8A')
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', '[COLOR gold]Series[/COLOR] Arabic', icons + '/Arabic.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA-%D9%87%D9%86%D8%AF%D9%8A%D8%A9')
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', '[COLOR gold]Series[/COLOR] Hindi', icons + '/Hindi.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%D8%A8%D8%B1%D8%A7%D9%85%D8%AC-%D8%AA%D9%84%D9%81%D8%B2%D9%8A%D9%88%D9%86%D9%8A%D8%A9')
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', '[COLOR gold]Series[/COLOR] TV Programs', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%D8%B9%D8%B1%D9%88%D8%B6-%D9%85%D8%B5%D8%A7%D8%B1%D8%B9%D8%A9')
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', '[COLOR gold]Series[/COLOR] Wrestling', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA-%D8%B1%D9%85%D8%B6%D8%A7%D9%86-2026')
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', '[COLOR gold]Series[/COLOR] Ramadan 2026', icons + '/Ramadan.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = URL_MAIN + '/search?s=' + urllib.parse.quote(sSearchText)
        _list_items(sUrl, oGui)
        oGui.setEndOfDirectory()

def showMovies(sSearch=''):
    oGui = cGui()
    if sSearch:
        sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')
    _list_items(sUrl, oGui)
    oGui.setEndOfDirectory()

def showSeries(sSearch=''):
    showMovies(sSearch)

def _list_items(sUrl, oGui):
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = r'<a href="(.+?)" class="show-card"[^>]*style="background-image: url\((.+?)\)[^>]*>[\s\S]*?<p class="title">([^<]+)</p>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            siteUrl = aEntry[0]
            sTitle = aEntry[2].strip()
            sThumb = aEntry[1]

            sYear = ''
            m = re.search(r'([0-9]{4})', sTitle)
            if m:
                sYear = m.group(1)
                sTitle = sTitle.replace(sYear, '').strip()

            oOutputParameterHandler.addParameter('siteUrl', siteUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('sYear', sYear)
            oOutputParameterHandler.addParameter('sDesc', '')

            if '/episode/' in siteUrl:
                oGui.addTV(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, '', oOutputParameterHandler)
            else:
                oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, '', oOutputParameterHandler)

def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    hosterAdded = False

    try:
        oReq = cRequestHandler(sUrl)
        oReq.setTimeout(20)
        detailHtml = oReq.request()
        if not detailHtml:
            VSlog('shiid4u showHosters: empty detail page')
            raise Exception('empty detail page')

        downloadUrl = ''

        patterns = [
            r'<a[^>]*href="([^"]*download[^"]*)"[^>]*class="btn download"',
            r'class="btn download"[^>]*href="([^"]*)"',
            r'class="download"[^>]*href="([^"]*)"',
            r'href="([^"]*/download/[^"]+)"',
        ]
        for pat in patterns:
            m = re.search(pat, detailHtml)
            if m:
                downloadUrl = m.group(1)
                break

        if not downloadUrl:
            slug = sUrl.rstrip('/').rsplit('/', 1)[-1]
            downloadUrl = URL_MAIN + '/download/' + slug
            VSlog('shiid4u showHosters: constructed download URL: ' + downloadUrl)

        if downloadUrl.startswith('/'):
            downloadUrl = URL_MAIN + downloadUrl

        VSlog('shiid4u showHosters: downloadUrl: ' + downloadUrl)
        oReq2 = cRequestHandler(downloadUrl)
        oReq2.setTimeout(20)
        downloadHtml = oReq2.request()
        if not downloadHtml:
            VSlog('shiid4u showHosters: empty download page')
            raise Exception('empty download page')

        urlPattern = r'href="(https?://(?!shiid4u\.co)[^"]+)"'
        oParser = cParser()
        aResult = oParser.parse(downloadHtml, urlPattern)

        if aResult[0]:
            seen = set()
            for sEmbedUrl in aResult[1]:
                if sEmbedUrl in seen:
                    continue
                seen.add(sEmbedUrl)

                domain = sEmbedUrl.split('/')[2]
                if any(exclude in domain for exclude in ['fonts.googleapis', 'cdnjs', 'cloudflare', 'facebook', 'x.com', 'googleapis', 'gstatic']):
                    continue

                try:
                    sTitle = sMovieTitle + ' [COLOR violet]' + domain.split('.')[0].upper() + '[/COLOR]'

                    hmf = resolveurl.HostedMediaFile(url=sEmbedUrl)
                    if hmf.valid_url():
                        oHoster = cHosterGui().getHoster('resolver')
                        sHostName = sEmbedUrl.split('/')[2].replace('www.', '')
                        oHoster.setRealHost(sHostName.split('.')[0].upper())
                    else:
                        oHoster = cHosterGui().checkHoster(sEmbedUrl)

                    if oHoster:
                        oHoster.setDisplayName(sTitle)
                        oHoster.setFileName(sMovieTitle)
                        cHosterGui().showHoster(oGui, oHoster, sEmbedUrl, sThumb)
                        hosterAdded = True
                except Exception as e:
                    VSlog('shiid4u showHosters: error processing URL ' + sEmbedUrl + ': ' + str(e))
                    continue
    except Exception as e:
        VSlog('shiid4u showHosters error: ' + str(e))

    if not hosterAdded:
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]No links found[/COLOR]')

    oGui.setEndOfDirectory()
