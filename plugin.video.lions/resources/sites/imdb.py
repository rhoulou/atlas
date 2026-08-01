# -*- coding: utf-8 -*-
# IMDb browse site (scrape www.imdb.com + legacy suggestion API for search)

import re
import json
import urllib.parse

from resources.lib.comaddon import addon, siteManager
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler

SITE_IDENTIFIER = 'imdb'
SITE_NAME = '[COLOR yellow]IMDb[/COLOR]'
SITE_DESC = 'Internet Movie Database.'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

SUGGEST_URL = 'https://v2.sg.media-imdb.com/suggestion/'

MOVIE_TOP250 = (URL_MAIN + 'chart/top/', 'showMovies')
MOVIE_POPULAR = (URL_MAIN + 'chart/moviemeter/', 'showMovies')
SERIE_POPULAR = (URL_MAIN + 'chart/tvmeter/', 'showSeries')

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/imdb.png'

GENRES = [
    ('Action', 'action'),
    ('Aventure', 'adventure'),
    ('Animation', 'animation'),
    ('Comedie', 'comedy'),
    ('Crime', 'crime'),
    ('Documentaire', 'documentary'),
    ('Drame', 'drama'),
    ('Famille', 'family'),
    ('Fantastique', 'fantasy'),
    ('Histoire', 'history'),
    ('Horreur', 'horror'),
    ('Musique', 'music'),
    ('Mystere', 'mystery'),
    ('Romance', 'romance'),
    ('Science-Fiction', 'sci-fi'),
    ('Thriller', 'thriller'),
    ('Western', 'western')
]


def load():
    oGui = cGui()
    addons = addon()
    icons = addons.getSetting('defaultIcons')
    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', addons.VSlang(30330), icons + '/Search.png', oOutputParameterHandler)

    oOutputParameterHandler.addParameter('siteUrl', MOVIE_TOP250[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_TOP250[1], 'Top 250', LOGO, oOutputParameterHandler)

    oOutputParameterHandler.addParameter('siteUrl', MOVIE_POPULAR[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_POPULAR[1], 'Films Populaires', LOGO, oOutputParameterHandler)

    oOutputParameterHandler.addParameter('siteUrl', SERIE_POPULAR[0])
    oGui.addDir(SITE_IDENTIFIER, SERIE_POPULAR[1], 'Series Populaires', LOGO, oOutputParameterHandler)

    oOutputParameterHandler.addParameter('siteUrl', 'http://venom')
    oGui.addDir(SITE_IDENTIFIER, 'showGenres', addons.VSlang(30428), icons + '/Genres.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showGenres():
    oGui = cGui()
    oOutputParameterHandler = cOutputParameterHandler()
    for sLabel, sGenre in GENRES:
        sUrl = URL_MAIN + 'search/title/?title_type=feature&genres=' + sGenre + '&sort=moviemeter,asc'
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oGui.addDir(SITE_IDENTIFIER, 'showMovies', sLabel, icons + '/Genres.png', oOutputParameterHandler)
    oGui.setEndOfDirectory()


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if not sSearchText:
        oGui.setEndOfDirectory()
        return
    showSearchResults(sSearchText)
    oGui.setEndOfDirectory()


def showSearchResults(sSearchText=''):
    oGui = cGui()
    if not sSearchText:
        oGui.setEndOfDirectory()
        return

    sSearchText = re.sub(' +', ' ', sSearchText)
    sTerm = urllib.parse.quote_plus(sSearchText)
    sFirst = sTerm[0].lower()
    sUrl = SUGGEST_URL + sFirst + '/' + sTerm + '.json'

    oRequestHandler = cRequestHandler(sUrl)
    oRequestHandler.addHeaderEntry('Accept-Language', 'en-US,en;q=0.9')
    data = oRequestHandler.request(jsonDecode=True)

    if not data or 'd' not in data:
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]Aucun résultat n\'a été trouvé.[/COLOR]')
        return

    for row in data['d']:
        sId = row.get('id', '')
        if not sId.startswith('tt'):
            continue
        sTitle = row.get('l', '')
        if not sTitle:
            continue
        sYear = row.get('y', '')
        sDesc = row.get('s', '')
        sThumb = ''
        sImage = row.get('i')
        if isinstance(sImage, dict):
            sThumb = sImage.get('imageUrl', '')
        sQid = row.get('qid', '')

        if sQid in ('tvSeries', 'tvMiniSeries'):
            oGui.addTV('globalSearch', 'showSearch', sTitle, '', sThumb, sDesc, __params(sTitle, sYear, sId))
        else:
            oGui.addMovie('globalSearch', 'showSearch', sTitle, '', sThumb, sDesc, __params(sTitle, sYear, sId))


def showMovies(sSearch=''):
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    if sSearch:
        sUrl = sSearch
    else:
        sUrl = oInputParameterHandler.getValue('siteUrl')

    aRows = __getRows(sUrl)
    if not aRows:
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]Aucun résultat n\'a été trouvé.[/COLOR]')
        oGui.setEndOfDirectory()
        return

    for aRow in aRows:
        sTitle, sYear, sThumb, sFanart, sRating, sDesc, sId = aRow
        sLabel = sTitle
        if sRating:
            sLabel = '%s [COLOR fuchsia]%s/10[/COLOR]' % (sTitle, sRating)
        oGui.addMovie('globalSearch', 'showSearch', sLabel, '', sThumb, sDesc, __params(sTitle, sYear, sId))

    sNextUrl = __getNextUrl(sUrl)
    if sNextUrl:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sNextUrl)
        oGui.addNext(SITE_IDENTIFIER, 'showMovies', 'Suivant', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showSeries(sSearch=''):
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    if sSearch:
        sUrl = sSearch
    else:
        sUrl = oInputParameterHandler.getValue('siteUrl')

    aRows = __getRows(sUrl)
    if not aRows:
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]Aucun résultat n\'a été trouvé.[/COLOR]')
        oGui.setEndOfDirectory()
        return

    for aRow in aRows:
        sTitle, sYear, sThumb, sFanart, sRating, sDesc, sId = aRow
        sLabel = sTitle
        if sRating:
            sLabel = '%s [COLOR fuchsia]%s/10[/COLOR]' % (sTitle, sRating)
        oGui.addTV('globalSearch', 'showSearch', sLabel, '', sThumb, sDesc, __params(sTitle, sYear, sId))

    sNextUrl = __getNextUrl(sUrl)
    if sNextUrl:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sNextUrl)
        oGui.addNext(SITE_IDENTIFIER, 'showSeries', 'Suivant', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def __params(sTitle, sYear, sId):
    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom')
    oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
    oOutputParameterHandler.addParameter('sImdbId', sId)
    oOutputParameterHandler.addParameter('sYear', sYear)
    oOutputParameterHandler.addParameter('searchtext', sTitle)
    return oOutputParameterHandler


def __getHtml(sUrl):
    oRequestHandler = cRequestHandler(sUrl)
    oRequestHandler.addHeaderEntry('Accept-Language', 'en-US,en;q=0.9')
    oRequestHandler.addHeaderEntry('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    oRequestHandler.addHeaderEntry('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8')
    return oRequestHandler.request()


def __getRows(sUrl):
    sHtmlContent = __getHtml(sUrl)
    if not sHtmlContent:
        return None

    aRows = __jsonRows(sHtmlContent)
    if aRows is None:
        aRows = __regexRows(sHtmlContent)
    return aRows


def __jsonRows(sHtmlContent):
    oMatch = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', sHtmlContent, re.S)
    if not oMatch:
        return None
    try:
        data = json.loads(oMatch.group(1))
    except Exception:
        return None

    aTitles = []
    __collectTitleRows(data, aTitles)
    if not aTitles:
        return None

    aRows = []
    for row in aTitles:
        sId = row.get('id', '')
        sTitle = ''
        if isinstance(row.get('titleText'), dict):
            sTitle = row['titleText'].get('text', '')
        if not sTitle:
            sTitle = row.get('title', '') or row.get('l', '')

        sYear = ''
        if isinstance(row.get('releaseYear'), dict):
            sYear = row['releaseYear'].get('year', '')
        if not sYear:
            sYear = row.get('y', '')

        sThumb = ''
        sFanart = ''
        sImage = row.get('primaryImage') or row.get('image') or row.get('i')
        if isinstance(sImage, dict):
            sThumb = sImage.get('url', '') or sImage.get('imageUrl', '')
            sFanart = sThumb

        sRating = ''
        if isinstance(row.get('ratingsSummary'), dict):
            sRating = row['ratingsSummary'].get('aggregateRating', '')
        if not sRating:
            sRating = row.get('rating', '')

        sDesc = ''
        if isinstance(row.get('plot'), dict):
            sPlot = row['plot'].get('plotText', '')
            if isinstance(sPlot, dict):
                sDesc = sPlot.get('plainText', '')
        if not sDesc:
            sDesc = row.get('plot', '') if isinstance(row.get('plot', ''), str) else ''

        aRows.append((sTitle, sYear, sThumb, sFanart, str(sRating), sDesc, sId))
    return aRows


def __collectTitleRows(obj, aOut):
    if isinstance(obj, dict):
        sId = obj.get('id')
        if isinstance(sId, str) and re.match(r'^tt\d+$', sId):
            if any(k in obj for k in ('titleText', 'title', 'l')):
                aOut.append(obj)
        for v in obj.values():
            __collectTitleRows(v, aOut)
    elif isinstance(obj, list):
        for item in obj:
            __collectTitleRows(item, aOut)


def __regexRows(sHtmlContent):
    aRows = []
    sPattern = 'href="/title/(tt[0-9]+)/[^"]*"[^>]*>.*?alt="([^"]+)".*?src="([^"]+)"'
    oParser = __getParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if not aResult[0]:
        return None

    for aEntry in aResult[1]:
        sId, sTitle, sThumb = aEntry[0], aEntry[1], aEntry[2]
        sYear = ''
        oYear = re.search(r'\(([0-9]{4})\)', sHtmlContent[max(0, sHtmlContent.find(sTitle) - 200):sHtmlContent.find(sTitle) + 300])
        if oYear:
            sYear = oYear.group(1)
        sRating = ''
        oRating = re.search(r'ipc-rating-star--rating[^>]*>\s*([0-9]+\.[0-9]+)', sHtmlContent[max(0, sHtmlContent.find(sTitle) - 300):sHtmlContent.find(sTitle) + 300])
        if oRating:
            sRating = oRating.group(1)
        aRows.append((sTitle, sYear, sThumb, sThumb, sRating, '', sId))
    return aRows


def __getParser():
    from resources.lib.parser import cParser
    return cParser()


def __getNextUrl(sUrl):
    if 'search/title' not in sUrl:
        return None
    oMatch = re.search(r'[?&]start=([0-9]+)', sUrl)
    if oMatch:
        iStart = int(oMatch.group(1)) + 50
        return re.sub(r'([?&])start=[0-9]+', r'\1start=%d' % iStart, sUrl)
    if '?' in sUrl:
        return sUrl + '&start=51'
    return sUrl + '?start=51'
