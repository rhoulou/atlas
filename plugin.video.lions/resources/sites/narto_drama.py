# -*- coding: utf-8 -*-
# zombi https://github.com/zombiB/zombi-addons/

import re
import json
import urllib.parse
import html as html_mod

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import VSlog, siteManager, addon

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/sites/logos/narto_drama.png'

TimeOut = 60
SITE_IDENTIFIER = 'narto_drama'
SITE_NAME = 'Narto Drama'
SITE_DESC = 'arabic vod'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

SERIE_SERIES = (URL_MAIN, 'showSeries')
SERIE_MOVIES = (URL_MAIN + '?lang=ar-SA&type=movie-series', 'showSeries')
SERIE_ANIME = (URL_MAIN + '?lang=ar-SA&type=anime', 'showSeries')
SERIE_FEATURED = (URL_MAIN + 'featured?lang=ar-SA', 'showSeries')

URL_SEARCH = (URL_MAIN + 'search?q=', 'showSeriesSearch')
URL_SEARCH_SERIES = (URL_MAIN + 'search?q=', 'showSeriesSearch')
FUNCTION_SEARCH = 'showSeriesSearch'


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
    s = html_mod.unescape(title)
    s = re.sub(r'\s*-\s*مشاهدة مجانية\s*$', '', s)
    s = re.sub(r'\s*الحلقة.*$', '', s)
    s = re.sub(r'\s*[\uff08][^\uff09]*[\uff09]\s*', '', s)
    s = re.sub(r'\(.*?\)\s*', '', s)
    s = re.sub(r'\[.*?\]\s*', '', s)
    for phrase in ['مشاهدة مسلسل ', 'مشاهدة فيلم ', 'مشاهدة انمي ',
                   'مدبلج كامل', 'مترجم كامل', 'كاملة', ' كامل',
                   'جميع الحلقات', 'أون لاين', 'كل الحلقات']:
        s = s.replace(phrase, '')
    return s.strip(' -–—|"\'').strip()


# --- Menu ---

def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIE_SERIES[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'الرئيسية', icons + '/TVShows.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIE_MOVIES[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'أفلام ومسلسلات', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIE_ANIME[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'أنمي', icons + '/TVShows.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIE_FEATURED[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مميز', icons + '/TVShows.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN)
    oGui.addDir(SITE_IDENTIFIER, 'showProviders', 'المزودون', LOGO, oOutputParameterHandler)

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

    if '/search' in sUrl or '&q=' in sUrl or '?q=' in sUrl:
        oRequestHandler = cRequestHandler(sUrl)
        oRequestHandler.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
        sJsonContent = oRequestHandler.request()

        try:
            data = json.loads(sJsonContent)
        except Exception:
            oGui.setEndOfDirectory()
            return

        if not data.get('ok'):
            oGui.setEndOfDirectory()
            return

        items = data.get('items', [])
        oOutputParameterHandler = cOutputParameterHandler()
        for item in items:
            sTitle = clean_title_type(item.get('title', ''))
            sTitle = strip_tashkeel(sTitle).strip()
            sItemUrl = item.get('url', '')
            sThumb = item.get('poster_url', '')
            if sThumb and not sThumb.startswith('http'):
                sThumb = URL_MAIN.rstrip('/') + sThumb
            if not sTitle or not sItemUrl:
                continue

            oOutputParameterHandler.addParameter('siteUrl', sItemUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            oGui.addTV(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, sTitle, oOutputParameterHandler)
    else:
        showSeries(sUrl)

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

    sPattern = r'<article[^>]*class="card"[^>]*data-watch-url="([^"]*)"[^>]*data-movie-id="(\d+)"[^>]*data-movie-title="([^"]*)"'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            siteUrl = html_mod.unescape(aEntry[0])
            movieId = aEntry[1]
            sTitle = clean_title_type(html_mod.unescape(aEntry[2]))
            sTitle = strip_tashkeel(sTitle).strip()
            sThumb = ''

            aImg = re.search(
                r'data-watch-url="%s"[^>]*>.*?<img[^>]+src="([^"]+)"' % re.escape(aEntry[0]),
                sHtmlContent, re.DOTALL
            )
            if aImg:
                sThumb = aImg.group(1)
            if not sThumb and movieId:
                sThumb = URL_MAIN.rstrip('/') + '/assets/poster/' + movieId + '.webp'
            if sThumb and not sThumb.startswith('http'):
                sThumb = URL_MAIN.rstrip('/') + sThumb

            oOutputParameterHandler.addParameter('siteUrl', siteUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            oGui.addTV(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, sTitle, oOutputParameterHandler)

        sNextPage = __checkForNextPage(sHtmlContent)
        if sNextPage:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showSeries', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def __checkForNextPage(sHtmlContent):
    sPattern = r'class=["\']pager-link["\'][^>]*href=["\']([^"\']+)["\']'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        return aResult[1][0]
    return False


# --- Series detail -> episode list ---

def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle') or ''
    sThumb = oInputParameterHandler.getValue('sThumb') or ''

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sRealUrl = oRequestHandler.getRealUrl() or sUrl
    if sRealUrl:
        sUrl = sRealUrl

    sDesc = ''
    mDesc = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', sHtmlContent)
    if mDesc:
        sDesc = html_mod.unescape(mDesc.group(1)).strip()

    sPattern = r'<a[^>]*class="episode-item"[^>]*href="([^"]*)"[^>]*title="([^"]*)"'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        episodeCount = len(aResult[1])
        for aEntry in aResult[1]:
            epUrl = html_mod.unescape(aEntry[0])
            epTitle = html_mod.unescape(aEntry[1])

            epNum = ''
            mNum = re.search(r'/(\d+)\?lang=', epUrl)
            if mNum:
                epNum = mNum.group(1)

            displayTitle = sMovieTitle + ' - ' + (epTitle if epTitle else 'EP ' + epNum)

            oOutputParameterHandler.addParameter('siteUrl', sUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('sEpisodeUrl', epUrl)
            oOutputParameterHandler.addParameter('sEpisodeNum', epNum)
            oOutputParameterHandler.addParameter('sDesc', sDesc)

            if episodeCount > 1:
                oOutputParameterHandler.addParameter('sourceName', SITE_IDENTIFIER)
                oOutputParameterHandler.addParameter('saisonUrl', sUrl)
                oOutputParameterHandler.addParameter('nextSaisonFunc', 'showHosters')
                oOutputParameterHandler.addParameter('sSeason', '1')
                oOutputParameterHandler.addParameter('sEpisode', epNum)

            oGui.addDir(SITE_IDENTIFIER, 'playEpisode', displayTitle, sThumb, oOutputParameterHandler)
    else:
        if '?' in sUrl:
            epUrl = sUrl.split('?')[0] + '/1?' + sUrl.split('?', 1)[1]
        else:
            epUrl = sUrl + '/1'
        epNum = '1'

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle)
        oOutputParameterHandler.addParameter('sThumb', sThumb)
        oOutputParameterHandler.addParameter('sEpisodeUrl', epUrl)
        oOutputParameterHandler.addParameter('sEpisodeNum', epNum)
        oOutputParameterHandler.addParameter('sDesc', sDesc)
        oGui.addDir(SITE_IDENTIFIER, 'playEpisode', sMovieTitle, sThumb, oOutputParameterHandler)

    oGui.setEndOfDirectory()


# --- Provider explorer ---

PROVIDERS_API = URL_MAIN + 'home/providers/sections'


def _fetchProvidersApi(provider_key, tab_pages=None):
    params = {'provider': provider_key, 'lang': 'ar-SA'}
    if tab_pages:
        for tk, pg in tab_pages.items():
            params['tab_pages[%s]' % tk] = str(pg)
    url = PROVIDERS_API + '?' + urllib.parse.urlencode(params)
    oRequest = cRequestHandler(url)
    oRequest.addHeaderEntry('Accept', 'application/json')
    oRequest.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
    oRequest.addHeaderEntry('Referer', URL_MAIN)
    oRequest.addHeaderEntry('Origin', URL_MAIN.rstrip('/'))
    try:
        return json.loads(oRequest.request())
    except Exception:
        return None


def showProviders():
    oGui = cGui()
    data = _fetchProvidersApi('netshort')
    if not data or not data.get('ok'):
        oGui.setEndOfDirectory()
        return

    providers = data.get('providers', [])
    oOutputParameterHandler = cOutputParameterHandler()
    for prov in providers:
        key = prov.get('key', '')
        label = prov.get('label', key)
        if not key:
            continue
        oOutputParameterHandler.addParameter('providerKey', key)
        oOutputParameterHandler.addParameter('providerLabel', label)
        oOutputParameterHandler.addParameter('siteUrl', URL_MAIN)
        oGui.addDir(SITE_IDENTIFIER, 'showProviderSections', label, LOGO, oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showProviderSections():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    providerKey = oInputParameterHandler.getValue('providerKey')
    providerLabel = oInputParameterHandler.getValue('providerLabel')

    data = _fetchProvidersApi(providerKey)
    if not data or not data.get('ok'):
        oGui.setEndOfDirectory()
        return

    sections = data.get('sections', [])
    oOutputParameterHandler = cOutputParameterHandler()
    for sec in sections:
        tabKey = sec.get('tab_key', '')
        tabLabel = sec.get('tab_label', tabKey)
        if not tabKey:
            continue
        oOutputParameterHandler.addParameter('providerKey', providerKey)
        oOutputParameterHandler.addParameter('providerLabel', providerLabel)
        oOutputParameterHandler.addParameter('tabKey', tabKey)
        oOutputParameterHandler.addParameter('tabLabel', tabLabel)
        oOutputParameterHandler.addParameter('page', '1')
        oOutputParameterHandler.addParameter('siteUrl', URL_MAIN)
        oGui.addDir(SITE_IDENTIFIER, 'showProviderItems', tabLabel, LOGO, oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showProviderItems():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    providerKey = oInputParameterHandler.getValue('providerKey')
    providerLabel = oInputParameterHandler.getValue('providerLabel')
    tabKey = oInputParameterHandler.getValue('tabKey')
    tabLabel = oInputParameterHandler.getValue('tabLabel')
    page = int(oInputParameterHandler.getValue('page') or '1')

    tabPages = {tabKey: page}
    data = _fetchProvidersApi(providerKey, tabPages)
    if not data or not data.get('ok'):
        oGui.setEndOfDirectory()
        return

    sections = data.get('sections', [])
    targetSection = None
    for sec in sections:
        if sec.get('tab_key') == tabKey:
            targetSection = sec
            break

    if not targetSection:
        oGui.setEndOfDirectory()
        return

    items = targetSection.get('items', [])
    hasPrev = targetSection.get('has_prev', False)

    oOutputParameterHandler = cOutputParameterHandler()
    for item in items:
        sTitle = clean_title_type(item.get('title', ''))
        sTitle = strip_tashkeel(sTitle).strip()
        sItemUrl = item.get('watch_url', '')
        sThumb = item.get('poster_url', '')
        sDesc = item.get('description', '')
        isAdult = item.get('is_adult', False)

        if not sTitle or not sItemUrl:
            continue

        oOutputParameterHandler.addParameter('siteUrl', sItemUrl)
        oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
        oOutputParameterHandler.addParameter('sThumb', sThumb)

        oGui.addTV(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, sTitle, oOutputParameterHandler)

    if hasPrev and page > 1:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('providerKey', providerKey)
        oOutputParameterHandler.addParameter('providerLabel', providerLabel)
        oOutputParameterHandler.addParameter('tabKey', tabKey)
        oOutputParameterHandler.addParameter('tabLabel', tabLabel)
        oOutputParameterHandler.addParameter('page', str(page - 1))
        oOutputParameterHandler.addParameter('siteUrl', URL_MAIN)
        oGui.addDir(SITE_IDENTIFIER, 'showProviderItems', '[COLOR teal]<<<_previous[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    if len(items) >= 10:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('providerKey', providerKey)
        oOutputParameterHandler.addParameter('providerLabel', providerLabel)
        oOutputParameterHandler.addParameter('tabKey', tabKey)
        oOutputParameterHandler.addParameter('tabLabel', tabLabel)
        oOutputParameterHandler.addParameter('page', str(page + 1))
        oOutputParameterHandler.addParameter('siteUrl', URL_MAIN)
        oGui.addDir(SITE_IDENTIFIER, 'showProviderItems', '[COLOR teal]next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


# --- Episode playback ---

def _buildHeaders(url, isHls):
    UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    headers = 'User-Agent=' + UA + '&Referer=' + URL_MAIN + '&Origin=' + URL_MAIN.rstrip('/')
    if isHls:
        headers += '&Content-Type=application/x-mpegURL'
    return url + '|' + headers


def _extractEpisodeItemsRaw(html):
    p = html.find('episodeItemsRaw')
    if p < 0:
        return None
    p = html.find('[', p)
    if p < 0:
        return None
    depth = 0
    in_str = False
    esc = False
    for i in range(p, min(p + 2000000, len(html))):
        c = html[i]
        if esc:
            esc = False
            continue
        if c == '\\' and in_str:
            esc = True
            continue
        if c == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return html[p:i + 1]
    return None


def playEpisode():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sSeriesUrl = oInputParameterHandler.getValue('siteUrl') or ''
    sEpisodeUrl = oInputParameterHandler.getValue('sEpisodeUrl') or ''
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle') or ''
    sThumb = oInputParameterHandler.getValue('sThumb') or ''
    sEpisodeNum = oInputParameterHandler.getValue('sEpisodeNum') or ''
    sDesc = oInputParameterHandler.getValue('sDesc') or ''

    sVideoUrl = ''
    isHls = False
    subUrl = ''

    if '/search/import' in sSeriesUrl or '/detail/dummy/' in sSeriesUrl:
        oResolveReq = cRequestHandler(sSeriesUrl)
        oResolveReq.request()
        sSeriesUrl = oResolveReq.getRealUrl() or sSeriesUrl

    resolved = resolveNarto(sSeriesUrl, sEpisodeNum)
    if resolved and resolved.get('url'):
        sVideoUrl = resolved['url']
        isHls = resolved.get('type') == 'hls'

    if not sVideoUrl:
        oRequestHandler = cRequestHandler(sEpisodeUrl)
        sHtmlContent = oRequestHandler.request()

        raw = _extractEpisodeItemsRaw(sHtmlContent)
        episodes = []
        if raw:
            try:
                episodes = json.loads(raw)
            except Exception:
                pass

        targetEp = int(sEpisodeNum) if sEpisodeNum else 0
        target = None
        for ep in episodes:
            n = ep.get('number') or ep.get('route_episode_number') or 0
            try:
                if int(n) == targetEp:
                    target = ep
                    break
            except (ValueError, TypeError):
                continue

        if target:
            sVideoUrl = target.get('direct_play_url') or target.get('play_url') or ''
            isHls = target.get('direct_play_is_hls', False) or sVideoUrl.endswith('.m3u8') or '/e/h/' in sVideoUrl or '/e/m/' in sVideoUrl

            subUrl = target.get('subtitle_url') or ''
            if not subUrl:
                multiSubs = target.get('multi_subtitles') or []
                for sub in multiSubs:
                    if sub.get('language_code') == 'ar-SA':
                        subUrl = sub.get('subtitle_url', '')
                        break

    if not sVideoUrl:
        oGui.setEndOfDirectory()
        return

    sVideoUrl = _buildHeaders(sVideoUrl, isHls)

    if subUrl and not subUrl.startswith('http'):
        subUrl = URL_MAIN.rstrip('/') + subUrl

    oHoster = cHosterGui().getHoster('lien_direct')
    sDisplayTitle = sMovieTitle + ' [COLOR coral]EP ' + sEpisodeNum + '[/COLOR]'
    oHoster.setDisplayName(sDisplayTitle)
    oHoster.setFileName(sMovieTitle)
    oHoster.sDescription = sDesc
    if subUrl:
        oHoster.setSubtitle(subUrl)
    cHosterGui().showHoster(oGui, oHoster, sVideoUrl, sThumb)

    oGui.setEndOfDirectory()


# --- Refresh-source resolver ---

def resolveNarto(sSeriesUrl, sEpisodeNum):
    m = re.search(r'/detail/watch/([^/?]+)', sSeriesUrl)
    if not m:
        return None
    slug = m.group(1)

    rsCtx = 'eyJtb3ZpZV9pZCI6NTcxMTksInNsdWciOiJ6LXltLWxtZnktbGtocy1ieSIsInN0cmVhbV9hcGkiOjEsInNvdXJjZV9hcHBfbmFtZSI6Im1vYm9yZWVscyIsInNvdXJjZV9ib29rX2lkIjoiNDk3MzY0MTUiLCJsYW5ndWFnZSI6ImFyLVNBIiwic3RvcmFnZV9iYWNrZW5kIjoicjIiLCJkb250X3JlZnJlc2hfc291cmNlIjowLCJleHAiOjE3ODM0ODUwNTl9.004057e0a3b3127ec3539e07beabf71cb7eccd76b309dbaaf35c6724fd644996'

    apiUrl = (
        'https://edge.narto-drama.com/e/rs/detail/watch/%s/%s/refresh-source'
        '?lang=ar-SA&rs_ctx=%s&force=1'
        % (slug, sEpisodeNum, urllib.parse.quote(rsCtx))
    )

    oRequest = cRequestHandler(apiUrl)
    oRequest.addHeaderEntry('Accept', 'application/json')
    oRequest.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
    oRequest.addHeaderEntry('Referer', URL_MAIN)
    oRequest.addHeaderEntry('Origin', URL_MAIN.rstrip('/'))
    sJsonContent = oRequest.request()

    try:
        data = json.loads(sJsonContent)
    except Exception:
        return None

    if not data.get('ok'):
        return None

    url = data.get('direct_play_url') or data.get('play_url') or ''
    isHls = (data.get('direct_play_is_hls', False) or url.endswith('.m3u8')
             or '/e/h/' in url or '/e/m/' in url)

    return {'url': url, 'type': 'hls' if isHls else 'mp4'}
