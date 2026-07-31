# -*- coding: utf-8 -*-
import re
import time
import requests
import urllib.parse

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.comaddon import VSlog, siteManager, addon

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/ok_ru.png'

SITE_IDENTIFIER = 'ok_ru'
SITE_NAME = 'OK.RU'
SITE_DESC = 'ok.ru search'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

URL_SEARCH_MOVIES = ('', 'showSearch')
URL_SEARCH_DRAMAS = ('', 'showSearch')
URL_SEARCH_SERIES = ('', 'showSearchSeries')

OKRU_URL = 'https://ok.ru'
OKRU_SEARCH_URL = OKRU_URL + '/video/search?st.cmd=video&st.psft=showcase&st.m=SEARCH&st.ft=search&st.fuvh=on&st.furl=%2Fvideo%2Fshowcase&cmd=VideoContentBlock'

MIN_MOVIE_DURATION = 1800

sUserAgent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36'


def _searchKeywords(sQuery):
    return [w.lower() for w in sQuery.split() if not re.match(r'^\d{4}$', w)]


def _matchesTitle(sTitle, aKeywords):
    if not aKeywords:
        return True
    sTitleLower = sTitle.lower()
    return all(w in sTitleLower for w in aKeywords)


def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search', icons + '/Search.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showSearch(sSearchText=''):
    __search(sSearchText, True)


def showSearchSeries(sSearchText=''):
    __search(sSearchText, False)


def __search(sSearchText, bMinDuration):
    oGui = cGui()

    bFromMenu = not sSearchText
    if bFromMenu:
        sSearchText = oGui.showKeyBoard()
        if not sSearchText:
            oGui.setEndOfDirectory()
            return False

    sSearchText = urllib.parse.unquote(sSearchText)
    aKeywords = _searchKeywords(sSearchText)
    aResults = []
    try:
        for aEntry in __searchOkRu(sSearchText):
            if not _matchesTitle(aEntry['title'], aKeywords):
                continue
            if bMinDuration and aEntry['duration'] < MIN_MOVIE_DURATION:
                continue
            aResults.append(aEntry)
    except Exception as e:
        VSlog('ok_ru: search failed (' + str(e) + ')')

    if not aResults:
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]No results[/COLOR]')

    for aEntry in aResults:
        sTitle = aEntry['title'].strip()
        sThumb = aEntry['thumb']
        sIcon = sThumb if sThumb else icons + '/Movies.png'
        sMin = int(aEntry['duration'] / 60)
        if sMin > 0:
            sDisplay = '%s [COLOR grey][%dmin][/COLOR] [COLOR violet]%s[/COLOR]' % (sTitle, sMin, aEntry['host'])
        else:
            sDisplay = '%s [COLOR violet]%s[/COLOR]' % (sTitle, aEntry['host'])

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', aEntry['url'])
        oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
        oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sDisplay, sIcon, sThumb, sDisplay, oOutputParameterHandler)

    if bFromMenu:
        oGui.setEndOfDirectory()


def __searchOkRu(sQuery):
    aResults = []
    oSession = requests.Session()
    oSession.headers.update({'User-Agent': sUserAgent, 'Accept-Language': 'en-US,en;q=0.5'})
    oSession.get(OKRU_URL, timeout=10)

    oHeaders = {
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded',
        'ok-screen': 'anonymVideo',
        'origin': OKRU_URL,
        'referer': OKRU_URL + '/video/showcase',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'strd': 'false',
        'strv': 'null',
        'tkn': 'undefined',
        'x-client-flags': 'ms:0;dcss:0;mpv2:1;dz:0'
    }
    oData = {'st.v.sq': sQuery, 'gwt.requested': 'daafbb8dT' + str(int(time.time() * 1000))}
    oResponse = oSession.post(OKRU_SEARCH_URL, data=oData, headers=oHeaders, timeout=15)
    sHtmlContent = oResponse.text

    dMovies = {}
    for oMatch in re.finditer(r'&quot;movie&quot;:\{&quot;href&quot;:&quot;/video/(\d+)', sHtmlContent):
        sId = oMatch.group(1)
        if sId in dMovies:
            continue
        sSeg = sHtmlContent[oMatch.start():oMatch.start() + 1700]
        oTitle = re.search(r'&quot;title&quot;:&quot;((?:[^\\]|\\.)+?)&quot;', sSeg)
        oDur = re.search(r'&quot;duration&quot;:(\d+)', sSeg)
        dMovies[sId] = {'title': __unescape(oTitle.group(1)) if oTitle else '?',
                        'dur': int(oDur.group(1)) if oDur else 0, 'img': ''}

    for oMatch in re.finditer(r'&quot;imageUrl&quot;:&quot;([^&]+?)&quot;,&quot;openMovieLink&quot;:&quot;/video/(\d+)', sHtmlContent):
        sImg, sId = oMatch.group(1), oMatch.group(2)
        if sId in dMovies and not dMovies[sId]['img']:
            dMovies[sId]['img'] = __unescape(sImg)

    for sId, oInfo in dMovies.items():
        aResults.append({'host': 'OK.RU', 'url': OKRU_URL + '/videoembed/' + sId,
                         'title': oInfo['title'], 'duration': oInfo['dur'] / 1000, 'thumb': oInfo['img']})
    return aResults


def __unescape(sText):
    return sText.replace('\\u0026', '&').replace('\\/', '/')


def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')

    sEmbedUrl = sUrl.split('|')[0]
    oHoster = None
    try:
        import resolveurl
        oHmf = resolveurl.HostedMediaFile(url=sEmbedUrl)
        if oHmf.valid_url():
            oHoster = cHosterGui().getHoster('resolver')
            sHost = sEmbedUrl.split('/')[2].replace('www.', '').split('.')[0].upper()
            oHoster.setRealHost(sHost)
    except Exception:
        pass

    if not oHoster:
        oHoster = cHosterGui().checkHoster(sEmbedUrl)

    if oHoster:
        oHoster.setDisplayName(sMovieTitle)
        oHoster.setFileName(sMovieTitle)
        cHosterGui().showHoster(oGui, oHoster, sEmbedUrl, '')

    oGui.setEndOfDirectory()
