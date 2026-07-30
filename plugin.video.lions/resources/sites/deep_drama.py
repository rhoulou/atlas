# -*- coding: utf-8 -*-
# zombi https://github.com/zombiB/zombi-addons/

import re
import urllib.parse
import json
import time
import base64
import html

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import VSlog, siteManager, addon

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/sites/logos/deep_drama.png'

# --- Title cleanup helpers ---

TASHKIL_RE = re.compile(r'[\u064B-\u0652\u0670\u0621]')


def strip_tashkeel(s):
    return TASHKIL_RE.sub('', s)


def detect_type(title):
    t = strip_tashkeel(title).lower()
    if any(w in t for w in ['انمي', 'أنمي', 'anime']):
        return 'anime'
    if any(w in t for w in ['فيلم', 'movie', 'فلم']):
        return 'movie'
    if any(w in t for w in ['مدبلج', 'dubbed']):
        return 'series'
    if any(w in t for w in ['مترجم', 'translated']):
        return 'series'
    if any(w in t for w in ['مسلسل', 'series', 'دراما']):
        return 'series'
    return ''


def clean_title_type(title):
    s = re.sub(r'\[.*?\]\s*', '', title)
    for phrase in ['مشاهدة مسلسل ', 'مشاهدة فيلم ', 'مشاهدة انمي ', 'مشاهدة برنامج ',
                   ' | ديب دراما', 'ديب دراما - ', 'ديب دراما',
                   'مترجم كامل جميع الحلقات أون لاين', 'مترجم كامل جميع الحلقات',
                   'مدبلج كامل مجاناً', 'مدبلج كامل', 'كاملة', ' كامل',
                   'جميع الحلقات أون لاين', 'جميع الحلقات', 'أون لاين', 'كل الحلقات']:
        s = s.replace(phrase, '')
    return s.strip(' -–—|').strip()


TimeOut = 60
SITE_IDENTIFIER = 'deep_drama'
SITE_NAME = 'Deep Drama'
SITE_DESC = 'arabic vod'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

SERIE_SERIES = (URL_MAIN, 'showSeries')
SERIE_TRANSLATED = (URL_MAIN + 'search/label/%D9%85%D8%B3%D9%84%D8%B3%D9%84%20%D9%85%D8%AA%D8%B1%D8%AC%D9%85', 'showSeries')
SERIE_DUBBED = (URL_MAIN + 'search/label/%D9%85%D8%B3%D9%84%D8%B3%D9%84%20%D9%85%D8%AF%D8%A8%D9%84%D8%AC', 'showSeries')
SERIE_CHINESE = (URL_MAIN + 'search/label/%D8%B5%D9%8A%D9%86%D9%8A', 'showSeries')
MOVIE_MOVIES = (URL_MAIN + 'search/label/%D9%81%D9%8A%D9%84%D9%85', 'showSeries')
SERIE_ACTION = (URL_MAIN + 'search/label/%D9%85%D8%B3%D9%84%D8%B3%D9%84%20%D8%A3%D9%83%D8%B4%D9%86', 'showSeries')
SERIE_ROMANCE = (URL_MAIN + 'search/label/%D9%85%D8%B3%D9%84%D8%B3%D9%84%20%D8%B1%D9%88%D9%85%D8%A7%D9%86%D8%B3%D9%8A', 'showSeries')
SERIE_DRAMA = (URL_MAIN + 'search/label/%D9%85%D8%B3%D9%84%D8%B3%D9%84%20%D8%AF%D8%B1%D8%A7%D9%85%D8%A7', 'showSeries')

URL_SEARCH = (URL_MAIN + 'search?q=', 'showSeriesSearch')
URL_SEARCH_SERIES = (URL_MAIN + 'search?q=', 'showSeriesSearch')
FUNCTION_SEARCH = 'showSeriesSearch'


def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIE_SERIES[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات', icons + '/TVShows.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIE_TRANSLATED[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات مترجمة', icons + '/TVShows.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIE_DUBBED[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات مدبلجة', icons + '/TVShows.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIE_CHINESE[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات صينية', icons + '/TVShows.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_MOVIES[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'أفلام', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIE_ACTION[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات أكشن', icons + '/TVShows.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIE_ROMANCE[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات رومانسي', icons + '/TVShows.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIE_DRAMA[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات دراما', icons + '/TVShows.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = URL_SEARCH[0] + urllib.parse.quote(sSearchText)
        showSeriesSearch(sUrl)
        oGui.setEndOfDirectory()


def showSeriesSearch(sSearch=''):
    oGui = cGui()
    if sSearch:
        sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = '<article class=.xr-card[^>\']*.[^<]*<a href=.([^\'\"]+)[\'"].*?xr-card__title.>([^<]+)<'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            siteUrl = aEntry[0]
            sTitle = html.unescape(aEntry[1])
            sTitle = clean_title_type(sTitle)
            sTitle = strip_tashkeel(sTitle).strip()
            sThumb = ''

            aImg = re.search(r"href=['\"]%s['\"][^>]*>.*?<img[^>]+src=['\"]([^'\"]+)['\"]" % re.escape(siteUrl), sHtmlContent, re.DOTALL)
            if aImg:
                sThumb = aImg.group(1)

            oOutputParameterHandler.addParameter('siteUrl', siteUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            oGui.addTV(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, sTitle, oOutputParameterHandler)

        sNextPage = __checkForNextPage(sHtmlContent)
        if sNextPage:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showSeriesSearch', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    if not sSearch:
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

    sPattern = '<article class=.xr-card[^>\']*.[^<]*<a href=.([^\'\"]+)[\'"].*?xr-card__title.>([^<]+)<'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            siteUrl = aEntry[0]
            sTitle = html.unescape(aEntry[1])
            sTitle = clean_title_type(sTitle)
            sTitle = strip_tashkeel(sTitle).strip()
            sThumb = ''

            aImg = re.search(r"href=['\"]%s['\"][^>]*>.*?<img[^>]+src=['\"]([^'\"]+)['\"]" % re.escape(siteUrl), sHtmlContent, re.DOTALL)
            if aImg:
                sThumb = aImg.group(1)

            oOutputParameterHandler.addParameter('siteUrl', siteUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            oGui.addTV(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, sTitle, oOutputParameterHandler)

        sNextPage = __checkForNextPage(sHtmlContent)
        if sNextPage:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showSeries', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    if not sSearch:
        oGui.setEndOfDirectory()


def __checkForNextPage(sHtmlContent):
    sPattern = "href=['\"]([^'\"]+)['\"][^>]*id=['\"]load-more-btn['\"]"
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        return aResult[1][0]

    return False


def resolveVidaraa(url):
    UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    filecode = url.split('/')[-1]
    host = url.split('/')[2]

    oRequest = cRequestHandler(url)
    oRequest.addHeaderEntry('User-Agent', UA)
    oRequest.request()
    cookie = oRequest.GetCookies()

    time.sleep(1.5)

    api_url = "https://%s/api/stream" % host
    oRequest = cRequestHandler(api_url)
    oRequest.setRequestType(1)
    oRequest.addHeaderEntry('User-Agent', UA)
    oRequest.addHeaderEntry('Referer', url)
    oRequest.addHeaderEntry('Cookie', cookie)
    oRequest.addHeaderEntry('Content-Type', 'application/json')
    oRequest.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
    oRequest.addParametersLine(json.dumps({"filecode": filecode, "device": "android"}))

    result = json.loads(oRequest.request())
    if 'streaming_url' in result:
        return result['streaming_url'] + '|User-Agent=' + UA + '&Referer=' + url
    return None


def resolveVoe(url):
    UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0'
    oParser = cParser()

    oRequest = cRequestHandler(url)
    oRequest.addHeaderEntry('User-Agent', UA)
    sHtmlContent = oRequest.request()

    if 'const currentUrl' in sHtmlContent:
        m = re.search(r"window\.location\.href\s*=\s*'([^']+)", sHtmlContent)
        if m:
            url = m.group(1)
            oRequest = cRequestHandler(url)
            oRequest.addHeaderEntry('User-Agent', UA)
            sHtmlContent = oRequest.request()

    m = re.search(r'json">\["([^"]+)"]</script>\s*<script\s*src="([^"]+)', sHtmlContent)
    if m:
        host = url.split('//')[0] + '//' + url.split('//')[1].split('/')[0]
        js_url = host + m.group(2)
        code = m.group(1)

        oRequest = cRequestHandler(js_url)
        oRequest.addHeaderEntry('User-Agent', UA)
        js_content = oRequest.request()

        m2 = re.search(r"(\[(?:'\W{2}'[,\]]){1,9})", js_content)
        if m2:
            lut = [''.join([('\\' + x) if x in '.*+?^${}()|[]\\' else x for x in i]) for i in m2.group(0)[2:-2].split("','")]
            txt = ''
            for c in code:
                x = ord(c)
                if 64 < x < 91:
                    x = (x - 52) % 26 + 65
                elif 96 < x < 123:
                    x = (x - 84) % 26 + 97
                txt += chr(x)
            for i in lut:
                txt = re.sub(i, '', txt)
            ct = base64.b64decode(txt)
            txt = ''.join([chr(i - 3) for i in ct])
            txt = base64.b64decode(txt[::-1])
            data = json.loads(txt)
            for key in data:
                if key in ('file', 'source'):
                    return data[key] + '|User-Agent=' + UA
    return None


def resolveRumble(url):
    UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'

    m = re.search(r'rumble\.com/embed/([^/?]+)', url)
    if not m:
        m = re.search(r'rumble\.com/[^/]*-([a-z0-9]+)', url)
    if not m:
        return None
    video_id = m.group(1)

    api_url = 'https://rumble.com/embedJS/u3/?request=video&ver=2&v=%s' % video_id
    oRequest = cRequestHandler(api_url)
    oRequest.addHeaderEntry('User-Agent', UA)
    sJsonContent = oRequest.request()

    try:
        data = json.loads(sJsonContent)
    except Exception:
        return None

    ua = data.get('ua', {})

    hls = ua.get('hls', {})
    hls_auto = hls.get('auto', {})
    hls_url = hls_auto.get('url', '')
    if hls_url:
        return hls_url

    return None


def getHosterName(url):
    try:
        from urllib.parse import urlparse
        host = urlparse(url).hostname or url
        host = host.replace('www.', '')
        if 'rumble' in host: return 'Rumble'
        if 'voe' in host: return 'Voe'
        if 'vidara' in host: return 'Vidaraa'
        if 'drive.google' in host: return 'GDrive'
        return host
    except:
        return url


def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sDesc = ''
    mDesc = re.search(r"<template id='post-body-template'><div class=['\"]series['\"]>\s*<p>([^<]+)</p>", sHtmlContent)
    if mDesc:
        sDesc = html.unescape(mDesc.group(1)).strip()

    oParser = cParser()
    hoster_urls = set()

    sPattern = 'xr-server-btn[^"]*"[^>]*data-src="([^"]+)"'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        for aEntry in aResult[1]:
            hoster_urls.add(aEntry)

    sPattern = 'data-src="([^"]+)"[^>]*class=.xr-server-btn'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        for aEntry in aResult[1]:
            hoster_urls.add(aEntry)

    sPattern = 'iframe[^>]+src="([^"]+)"'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        for aEntry in aResult[1]:
            if 'deep-drama.com' in aEntry or 'blogger' in aEntry:
                continue
            hoster_urls.add(aEntry)

    for sHosterUrl in hoster_urls:
        if 'vidaraa.cc' in sHosterUrl or 'vidara.so' in sHosterUrl or 'vidara.to' in sHosterUrl:
            resolved = resolveVidaraa(sHosterUrl)
            if resolved:
                oHoster = cHosterGui().getHoster('lien_direct')
                sDisplayTitle = sMovieTitle + ' [COLOR coral](' + getHosterName(sHosterUrl) + ')[/COLOR]'
                oHoster.setDisplayName(sDisplayTitle)
                oHoster.setFileName(sMovieTitle)
                oHoster.sDescription = sDesc
                cHosterGui().showHoster(oGui, oHoster, resolved, sThumb)
            continue

        if 'voe.sx' in sHosterUrl or 'voe.' in sHosterUrl:
            resolved = resolveVoe(sHosterUrl)
            if resolved:
                oHoster = cHosterGui().getHoster('lien_direct')
                sDisplayTitle = sMovieTitle + ' [COLOR coral](' + getHosterName(sHosterUrl) + ')[/COLOR]'
                oHoster.setDisplayName(sDisplayTitle)
                oHoster.setFileName(sMovieTitle)
                oHoster.sDescription = sDesc
                cHosterGui().showHoster(oGui, oHoster, resolved, sThumb)
            continue

        if 'rumble.com' in sHosterUrl:
            resolved = resolveRumble(sHosterUrl)
            if resolved:
                oHoster = cHosterGui().getHoster('lien_direct')
                sDisplayTitle = sMovieTitle + ' [COLOR coral](' + getHosterName(sHosterUrl) + ')[/COLOR]'
                oHoster.setDisplayName(sDisplayTitle)
                oHoster.setFileName(sMovieTitle)
                oHoster.sDescription = sDesc
                cHosterGui().showHoster(oGui, oHoster, resolved, sThumb)
            continue

        oHoster = cHosterGui().checkHoster(sHosterUrl)
        if oHoster:
            sDisplayTitle = sMovieTitle + ' [COLOR coral](' + getHosterName(sHosterUrl) + ')[/COLOR]'
            oHoster.setDisplayName(sDisplayTitle)
            oHoster.setFileName(sMovieTitle)
            oHoster.sDescription = sDesc
            cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)

    oGui.setEndOfDirectory()
