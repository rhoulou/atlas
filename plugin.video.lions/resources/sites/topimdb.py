# -*- coding: utf-8 -*-
# Top IMDb (series) - lists the 100-series IMDb catalog from the IMDB Catalogs Stremio addon.

from resources.lib.gui.gui import cGui
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler

SITE_IDENTIFIER = 'topimdb'
SITE_NAME = 'Top IMDb Series'
SITE_DESC = 'Top series catalogue IMDb.'

CATALOG_BASE = 'https://1fe84bc728af-imdb-catalogs.baby-beamup.club'
CATALOG_SERIES = CATALOG_BASE + '/catalog/series/imdb-series-catalog.json'

LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/topimdb.png'


def load():
    oGui = cGui()

    aMetas = []
    try:
        oRequestHandler = cRequestHandler(CATALOG_SERIES)
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

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', 'http://venom')
        oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
        oOutputParameterHandler.addParameter('sImdbId', sId)
        oOutputParameterHandler.addParameter('sYear', sYear)
        oOutputParameterHandler.addParameter('searchtext', sTitle)
        oGui.addTV('globalSearch', 'showSearch', sTitle, '', sThumb, '', oOutputParameterHandler)
        bAdded = True

    if not bAdded:
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]Aucun résultat n\'a été trouvé.[/COLOR]')

    oGui.setEndOfDirectory()
