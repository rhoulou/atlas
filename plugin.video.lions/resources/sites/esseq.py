# -*- coding: utf-8 -*-

import re
import base64
import json

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import VSlog, siteManager, addon

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/sites/logos/esseq.png'

SITE_IDENTIFIER = 'esseq'
SITE_NAME = 'Esseq'
SITE_DESC = 'arabic vod'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

SERIE_TR = (URL_MAIN + 'all-series/', 'showSeries')
MOVIE_TURK = (URL_MAIN + 'category/yeni-filmler/', 'showMovies')
LATEST = (URL_MAIN + 'son-bolumler/', 'showMovies')

URL_SEARCH = (URL_MAIN + 'search/', 'showMovies')
URL_SEARCH_SERIES = (URL_MAIN + 'search/', 'showSeries')
FUNCTION_SEARCH = 'showMovies'

def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search Movies', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSeriesSearch', 'SEARCH_SERIES', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', LATEST[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'آخر الحلقات', icons + '/Turkish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_TURK[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام', icons + '/Turkish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIE_TR[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'جميع المسلسلات', icons + '/Turkish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + 'category/alarshif/')
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات كاملة', icons + '/Turkish.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = URL_MAIN + 'search/' + sSearchText
        showMovies(sUrl)
        oGui.setEndOfDirectory()
        return

def showSeriesSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = URL_MAIN + 'search/' + sSearchText
        showSeries(sUrl)
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
    sPattern = '<article class="post">.*?<a href="([^"]+)".*?<div class="imgBg" style="background-image:url\(([^)]+)\);"></div></div>.*?<div class="title">([^<]+)</div>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            siteUrl = aEntry[0]
            sThumb = aEntry[1]
            sTitle = aEntry[2].replace('مشاهدة', '').replace('فيلم', '').replace('مسلسل', '').replace('اون لاين', '').replace('اونلاين', '').replace('مترجمة', '').replace('مترجم', '').replace('مدبلج', '').replace('حصرى', '').replace('على اكثر من سيرفر', '').strip()

            sYear = ''
            m = re.search('([0-9]{4})', sTitle)
            if m:
                sYear = str(m.group(0))
                sTitle = sTitle.replace(sYear, '').strip()

            if sThumb.startswith('//'):
                sThumb = 'https:' + sThumb

            oOutputParameterHandler.addParameter('siteUrl', siteUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('sYear', sYear)

            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, '', oOutputParameterHandler)

    if not sSearch:
        sNextPage = __checkForNextPage(sHtmlContent)
        if sNextPage:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showSeries(sSearch=''):
    oGui = cGui()
    if sSearch:
        sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    oParser = cParser()
    sPattern = '<article class="postEp">.*?<a href="([^"]+)".*?<div class="imgSer" style="background-image:url\(([^)]+)\);"></div></div>.*?<div class="title">([^<]+)</div>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            siteUrl = aEntry[0]
            sThumb = aEntry[1]
            sTitle = aEntry[2].replace('مشاهدة', '').replace('مسلسل', '').replace('انمي', '').replace('مترجمة', '').replace('مترجم', '').replace('برنامج', '').replace('فيلم', '').replace('والأخيرة', '').replace('مدبلج للعربية', 'مدبلج').replace('والاخيرة', '').replace('كاملة', '').replace('حلقات كاملة', '').replace('اونلاين', '').replace('مباشرة', '').replace('انتاج ', '').replace('جودة عالية', '').replace('كامل', '').replace('HD', '').replace('السلسلة الوثائقية', '').replace('الفيلم الوثائقي', '').replace('اون لاين', '').strip()

            if sThumb.startswith('//'):
                sThumb = 'http:' + sThumb

            oOutputParameterHandler.addParameter('siteUrl', siteUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            oGui.addTV(SITE_IDENTIFIER, 'showEps', sTitle, '', sThumb, '', oOutputParameterHandler)

    if not sSearch:
        sNextPage = __checkForNextPage(sHtmlContent)
        if sNextPage:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showSeries', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showEps():
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = '<article class="postEp">.*?<a href="([^"]+)".*?<div class="imgSer" style="background-image:url\(([^)]+)\);"></div></div>.*?<div class="title">([^<]+)</div>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            siteUrl = aEntry[0]
            sTitle = aEntry[2].replace('مشاهدة', '').replace('مسلسل', '').replace('انمي', '').replace('مترجمة', '').replace('مترجم', '').replace('الموسم', ' S').replace('S ', 'S').replace('الحلقة ', ' E').replace('حلقة ', ' E')

            oOutputParameterHandler.addParameter('siteUrl', siteUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            oGui.addEpisode(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, '', oOutputParameterHandler)
    else:
        if 'قريباً في موقع قصة عشق' in sHtmlContent:
            oGui.addText('', 'Soon on Esseq - No Episodes Yet', icons + '/None.png')
        else:
            oGui.addText('', 'Error - No Episodes Found', icons + '/None.png')

    oGui.setEndOfDirectory()

def showHosters():
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = 'href="https://qesen\.net/watch\?post=([^"]+)"'
    aResult = re.findall(sPattern, sHtmlContent)

    if aResult:
        for sEncoded in aResult:
            try:
                sDecoded = base64.b64decode(sEncoded).decode('utf-8', errors='ignore')
                oData = json.loads(sDecoded)
                servers = oData.get('servers', [])
                code_daily = oData.get('codeDaily', '')

                for server in servers:
                    sName = server.get('name', 'server')
                    sId = server.get('id', '')

                    sHosterUrl = ''
                    if sId.startswith('http'):
                        sHosterUrl = sId
                    elif 'ok' in sName.lower():
                        sHosterUrl = 'https://www.ok.ru/videoembed/' + sId
                    elif 'estream' in sName.lower():
                        sHosterUrl = 'https://arabveturk.com/embed-' + sId + '.html'
                    elif 'youtube' in sName.lower():
                        sHosterUrl = 'https://www.youtube.com/watch?v=' + sId
                    elif 'dailymotion' in sName.lower():
                        sHosterUrl = 'https://www.dailymotion.com/embed/video/' + sId
                    else:
                        sHosterUrl = 'https://qesen.net/watch?post=' + sEncoded + '&server=' + sName

                    sDisplayTitle = sMovieTitle + ' [' + sName + ']'

                    oHoster = cHosterGui().checkHoster(sHosterUrl)
                    if oHoster:
                        oHoster.setDisplayName(sDisplayTitle)
                        oHoster.setFileName(sMovieTitle)
                        cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)
            except:
                pass

    oGui.setEndOfDirectory()

def __checkForNextPage(sHtmlContent):
    sPattern = "<a href='([^']+)' class='inactive'"
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        return aResult[1][0]
    return False
