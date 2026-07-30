# -*- coding: utf-8 -*-

import re
import requests
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
LOGO = 'special://home/addons/plugin.video.lions/resources/sites/logos/egybest.png'

SITE_IDENTIFIER = 'egybest'
SITE_NAME = 'EgyBest'
SITE_DESC = 'arabic vod'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)
API_URL = URL_MAIN.rstrip('/') + '/wp-json/wp/v2/'

MOVIE_EN = ('', 'showMovies', 187)
MOVIE_AR = ('', 'showMovies', 35273)
MOVIE_ASIAN = ('', 'showMovies', 196)
MOVIE_TR = ('', 'showMovies', 2809)
MOVIE_HI = ('', 'showMovies', 2477)
KID_MOVIES = ('', 'showMovies', 2467)

SERIE_EN = ('', 'showSeries', 156)
SERIE_TR = ('', 'showSeries', 2703)
SERIE_AR = ('', 'showSeries', 47683)
SERIE_ASIA = ('', 'showSeries', 2)

ANIM_MOVIES = ('', 'showMovies', 819)
ANIM_SERIES = ('', 'showSeries', 38)

URL_SEARCH = ('', 'showMovies')
FUNCTION_SEARCH = 'showMovies'

def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'SEARCH MOVIES', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('catId', MOVIE_EN[2])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام أجنبية', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('catId', MOVIE_AR[2])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام عربية', icons + '/Arabic.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('catId', MOVIE_ASIAN[2])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام أسيوية', icons + '/Asian.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('catId', MOVIE_TR[2])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام تركية', icons + '/Turkish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('catId', MOVIE_HI[2])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام هندية', icons + '/Hindi.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('catId', KID_MOVIES[2])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام كرتون', icons + '/Cartoon.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('catId', SERIE_EN[2])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات أجنبية', icons + '/TVShowsEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('catId', SERIE_AR[2])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات عربية', icons + '/Arabic.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('catId', SERIE_ASIA[2])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات أسيوية', icons + '/Asian.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('catId', SERIE_TR[2])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات تركية', icons + '/Turkish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('catId', ANIM_MOVIES[2])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام انمي', icons + '/Anime.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('catId', ANIM_SERIES[2])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات إنمي', icons + '/Anime.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        showMovies(sSearchText)
        oGui.setEndOfDirectory()
        return

def __fetch_posts(catId=None, search=None, page=1):
    params = {'_embed': '', 'per_page': 20, 'page': page}
    if catId:
        params['categories'] = catId
    if search:
        params['search'] = search

    try:
        r = requests.get(API_URL + 'posts', params=params, timeout=15)
        if r.status_code != 200:
            return [], 0
        data = r.json()
        total_pages = int(r.headers.get('X-WP-TotalPages', 1))
        return data, total_pages
    except:
        return [], 0

def showMovies(sSearch=''):
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    catId = oInputParameterHandler.getValue('catId')
    page = int(oInputParameterHandler.getValue('page') or 1)

    if sSearch:
        posts, total_pages = __fetch_posts(search=sSearch)
    elif catId:
        posts, total_pages = __fetch_posts(catId=catId, page=page)
    else:
        oGui.setEndOfDirectory()
        return

    oOutputParameterHandler = cOutputParameterHandler()
    for post in posts:
        siteUrl = post.get('link', '')
        sTitle = post.get('title', {}).get('rendered', '')
        if not sTitle or not siteUrl:
            continue

        sThumb = ''
        embedded = post.get('_embedded', {})
        media = embedded.get('wp:featuredmedia')
        if media and len(media) > 0:
            sThumb = media[0].get('source_url', '')

        sDisplay = sTitle.replace('مشاهدة', '').replace('فيلم', '').replace('اون لاين', '').replace('اونلاين', '').replace('مترجم', '').replace('مدبلج', '').replace('حصرى', '').replace('على اكثر من سيرفر', '').strip()

        sYear = ''
        m = re.search('([0-9]{4})', sDisplay)
        if m:
            sYear = str(m.group(0))
            sDisplay = sDisplay.replace(sYear, '').strip()

        oOutputParameterHandler.addParameter('siteUrl', siteUrl)
        oOutputParameterHandler.addParameter('sMovieTitle', sDisplay)
        oOutputParameterHandler.addParameter('sThumb', sThumb)
        oOutputParameterHandler.addParameter('sYear', sYear)

        oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sDisplay, '', sThumb, '', oOutputParameterHandler)

    if catId and page < total_pages:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('catId', catId)
        oOutputParameterHandler.addParameter('page', page + 1)
        oGui.addDir(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showSeries(sSearch=''):
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    catId = oInputParameterHandler.getValue('catId')
    page = int(oInputParameterHandler.getValue('page') or 1)

    if sSearch:
        posts, total_pages = __fetch_posts(search=sSearch)
    elif catId:
        posts, total_pages = __fetch_posts(catId=catId, page=page)
    else:
        oGui.setEndOfDirectory()
        return

    oOutputParameterHandler = cOutputParameterHandler()
    for post in posts:
        siteUrl = post.get('link', '')
        sTitle = post.get('title', {}).get('rendered', '')
        if not sTitle or not siteUrl:
            continue

        sThumb = ''
        embedded = post.get('_embedded', {})
        media = embedded.get('wp:featuredmedia')
        if media and len(media) > 0:
            sThumb = media[0].get('source_url', '')

        sDisplay = sTitle.replace('مشاهدة', '').replace('مسلسل', '').replace('اون لاين', '').replace('اونلاين', '').replace('مترجم', '').replace('مدبلج', '').replace('حصرى', '').strip()

        sYear = ''
        m = re.search('([0-9]{4})', sDisplay)
        if m:
            sYear = str(m.group(0))

        oOutputParameterHandler.addParameter('siteUrl', siteUrl)
        oOutputParameterHandler.addParameter('sMovieTitle', sDisplay)
        oOutputParameterHandler.addParameter('sThumb', sThumb)
        oOutputParameterHandler.addParameter('sYear', sYear)

        oGui.addTV(SITE_IDENTIFIER, 'showHosters', sDisplay, '', sThumb, '', oOutputParameterHandler)

    if catId and page < total_pages:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('catId', catId)
        oOutputParameterHandler.addParameter('page', page + 1)
        oGui.addDir(SITE_IDENTIFIER, 'showSeries', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showHosters():
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = "loadIframe\\(this, '([^']+)'\\)"
    aResult = re.findall(sPattern, sHtmlContent)

    for sHosterUrl in aResult:
        sDisplayTitle = sMovieTitle
        if 'streamtape' in sHosterUrl.lower():
            sDisplayTitle = sMovieTitle + ' [streamtape]'
        elif 'filemoon' in sHosterUrl.lower():
            sDisplayTitle = sMovieTitle + ' [filemoon]'
        elif 'doodstream' in sHosterUrl.lower() or 'dood' in sHosterUrl.lower():
            sDisplayTitle = sMovieTitle + ' [doodstream]'
        elif 'mixdrop' in sHosterUrl.lower():
            sDisplayTitle = sMovieTitle + ' [mixdrop]'
        elif 'uqload' in sHosterUrl.lower():
            sDisplayTitle = sMovieTitle + ' [uqload]'
        elif 'cybervynx' in sHosterUrl.lower():
            sDisplayTitle = sMovieTitle + ' [cybervynx]'
        else:
            sDisplayTitle = sMovieTitle + ' [server]'

        oHoster = cHosterGui().checkHoster(sHosterUrl)
        if oHoster:
            oHoster.setDisplayName(sDisplayTitle)
            oHoster.setFileName(sMovieTitle)
            cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)

    oGui.setEndOfDirectory()
