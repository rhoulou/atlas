# -*- coding: utf-8 -*-
# IMDb browse + search site.
# Browse lists come from the IMDB Catalogs Stremio addon (100 movies / 100 series, each with a real IMDb id);
# search uses the IMDb legacy suggestion API (www.imdb.com scraping is blocked with HTTP 202).

import re
import urllib.parse

from resources.lib.comaddon import addon
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler

SITE_IDENTIFIER = 'imdb'
SITE_NAME = '[COLOR yellow]IMDb[/COLOR]'
SITE_DESC = 'Internet Movie Database.'

CATALOG_BASE = 'https://1fe84bc728af-imdb-catalogs.baby-beamup.club'
CATALOG_MOVIE = CATALOG_BASE + '/catalog/movie/imdb-movie-catalog.json'
CATALOG_SERIES = CATALOG_BASE + '/catalog/series/imdb-series-catalog.json'

SUGGEST_URL = 'https://v2.sg.media-imdb.com/suggestion/'

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/imdb.png'


def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', ADDON.VSlang(30330), icons + '/Search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', CATALOG_MOVIE)
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'Films IMDb', icons + '/Movies.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', CATALOG_SERIES)
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'Series IMDb', icons + '/TVShows.png', oOutputParameterHandler)

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

        oOutputParameterHandler = __params(sTitle, sYear, sId)
        if sQid in ('tvSeries', 'tvMiniSeries'):
            oGui.addTV('globalSearch', 'showSearch', sTitle, '', sThumb, sDesc, oOutputParameterHandler)
        else:
            oGui.addMovie('globalSearch', 'showSearch', sTitle, '', sThumb, sDesc, oOutputParameterHandler)


def showMovies():
    __showCatalog('movie')


def showSeries():
    __showCatalog('series')


def __showCatalog(sType):
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    if not sUrl:
        sUrl = CATALOG_MOVIE if sType == 'movie' else CATALOG_SERIES

    aMetas = []
    try:
        oRequestHandler = cRequestHandler(sUrl)
        data = oRequestHandler.request(jsonDecode=True)
        if data and isinstance(data, dict) and 'metas' in data:
            aMetas = data['metas']
    except Exception:
        aMetas = []

    bAdded = False
    for meta in aMetas:
        sId = meta.get('id') or meta.get('imdb_id') or ''
        if not str(sId).startswith('tt'):
            continue
        sTitle = meta.get('name', '')
        if not sTitle:
            continue
        sYear = meta.get('year', '')
        sThumb = meta.get('poster', '')

        oOutputParameterHandler = __params(sTitle, sYear, sId)
        if sType == 'series':
            oGui.addTV('globalSearch', 'showSearch', sTitle, '', sThumb, '', oOutputParameterHandler)
        else:
            oGui.addMovie('globalSearch', 'showSearch', sTitle, '', sThumb, '', oOutputParameterHandler)
        bAdded = True

    if not bAdded:
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]Aucun résultat n\'a été trouvé.[/COLOR]')

    oGui.setEndOfDirectory()


def __params(sTitle, sYear, sId):
    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom')
    oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
    oOutputParameterHandler.addParameter('sImdbId', sId)
    oOutputParameterHandler.addParameter('sYear', sYear)
    oOutputParameterHandler.addParameter('searchtext', sTitle)
    return oOutputParameterHandler
