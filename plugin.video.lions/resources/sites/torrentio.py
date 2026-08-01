# -*- coding: utf-8 -*-
# Torrentio (Stremio) aggregator site - streams from 24 torrent providers.

import re
import urllib.parse

from resources.lib.comaddon import addon, VSlog
from resources.lib.gui.gui import cGui
from resources.lib.gui.hoster import cHosterGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler

SITE_IDENTIFIER = 'torrentio'
SITE_NAME = 'Torrentio'
SITE_DESC = 'Torrentio aggregator (YTS, EZTV, RARBG, 1337x, ThePirateBay, ...).'

URL_MAIN = 'https://torrentio.strem.fun/'

URL_SEARCH = ('', 'showSearch')
FUNCTION_SEARCH = 'showSearch'

SUGGEST_URL = 'https://v2.sg.media-imdb.com/suggestion/'

MAX_SEASONS = 15
MAX_EPISODES = 30

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/torrentio.png'


def load():
    oGui = cGui()
    addons = addon()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', addons.VSlang(30330), icons + '/Search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom')
    oOutputParameterHandler.addParameter('sType', 'movie')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Films', icons + '/Movies.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom')
    oOutputParameterHandler.addParameter('sType', 'series')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Series', icons + '/TVShows.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showSearch(sSearchText=''):
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sType = oInputParameterHandler.getValue('sType')

    if not sSearchText:
        sSearchText = oInputParameterHandler.getValue('searchtext')
    if not sSearchText:
        sSearchText = oGui.showKeyBoard()
    if not sSearchText:
        oGui.setEndOfDirectory()
        return

    try:
        sSearchText = urllib.parse.unquote(sSearchText)
    except Exception:
        pass

    __showSearchResults(sSearchText, sType)
    oGui.setEndOfDirectory()


def __showSearchResults(sSearchText, sTypeFilter=''):
    oGui = cGui()
    sSearchText = re.sub(' +', ' ', sSearchText)
    sTerm = urllib.parse.quote_plus(sSearchText)
    sFirst = sTerm[0].lower()
    sUrl = SUGGEST_URL + sFirst + '/' + sTerm + '.json'

    oRequestHandler = cRequestHandler(sUrl)
    oRequestHandler.addHeaderEntry('Accept-Language', 'en-US,en;q=0.9')
    try:
        data = oRequestHandler.request(jsonDecode=True)
    except Exception as e:
        VSlog('torrentio: suggestion failed (%s)' % str(e))
        data = None

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

        sType = 'series' if sQid in ('tvSeries', 'tvMiniSeries') else 'movie'
        if sTypeFilter and sType != sTypeFilter:
            continue
        oOutputParameterHandler = __params(sTitle, sYear, sId, sType)
        if sType == 'series':
            oGui.addTV(SITE_IDENTIFIER, 'showSeasons', sTitle, '', sThumb, sDesc, oOutputParameterHandler)
        else:
            oGui.addMovie(SITE_IDENTIFIER, 'showStreams', sTitle, '', sThumb, sDesc, oOutputParameterHandler)


def showSeasons():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sImdbId = oInputParameterHandler.getValue('sImdbId')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')

    for i in range(1, MAX_SEASONS + 1):
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('sImdbId', sImdbId)
        oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle)
        oOutputParameterHandler.addParameter('sType', 'series')
        oOutputParameterHandler.addParameter('sSeason', str(i))
        oGui.addDir(SITE_IDENTIFIER, 'showEpisodes', 'Season %d' % i, icons + '/TVShows.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showEpisodes():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sImdbId = oInputParameterHandler.getValue('sImdbId')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sSeason = oInputParameterHandler.getValue('sSeason')

    for i in range(1, MAX_EPISODES + 1):
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('sImdbId', sImdbId)
        oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle)
        oOutputParameterHandler.addParameter('sType', 'series')
        oOutputParameterHandler.addParameter('sSeason', sSeason)
        oOutputParameterHandler.addParameter('sEpisode', str(i))
        oGui.addDir(SITE_IDENTIFIER, 'showStreams', 'Episode %d' % i, icons + '/TVShows.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showStreams():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sImdbId = oInputParameterHandler.getValue('sImdbId')
    sType = oInputParameterHandler.getValue('sType') or 'movie'
    sSeason = oInputParameterHandler.getValue('sSeason')
    sEpisode = oInputParameterHandler.getValue('sEpisode')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')

    if sType == 'series' and sSeason and sEpisode:
        sApiUrl = URL_MAIN + 'stream/series/%s:%s:%s.json' % (sImdbId, sSeason, sEpisode)
    else:
        sApiUrl = URL_MAIN + 'stream/movie/%s.json' % sImdbId

    oRequestHandler = cRequestHandler(sApiUrl)
    try:
        data = oRequestHandler.request(jsonDecode=True)
    except Exception as e:
        VSlog('torrentio: stream request failed (%s)' % str(e))
        data = None

    aStreams = []
    if data and isinstance(data, dict) and 'streams' in data:
        aStreams = data['streams']

    bAdded = False
    for stream in aStreams:
        sInfoHash = stream.get('infoHash', '')
        if not sInfoHash:
            continue
        sLabel, sPlainName = __buildLabel(stream)
        sFileIdx = stream.get('fileIdx')

        magnet = 'magnet:?xt=urn:btih:%s&dn=%s' % (sInfoHash, urllib.parse.quote(sPlainName, safe=''))
        encoded = urllib.parse.quote(magnet, safe=':/?&=%')
        elementumUrl = 'plugin://plugin.video.elementum/play?uri=' + encoded
        if sFileIdx not in (None, ''):
            elementumUrl += '&fileIndex=' + str(sFileIdx)

        oHoster = cHosterGui().getHoster('elementum')
        oHoster.setDisplayName(sLabel)
        oHoster.setFileName(sLabel if sMovieTitle in (None, '') else sMovieTitle)
        cHosterGui().showHoster(oGui, oHoster, elementumUrl, '')
        bAdded = True

    if not bAdded:
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]Aucun stream trouvé.[/COLOR]')

    oGui.setEndOfDirectory()


def __buildLabel(stream):
    sName = stream.get('name', '')
    sTitle = stream.get('title', '')

    sQuality = ''
    aName = [x.strip() for x in str(sName).split('\n') if x.strip()]
    if len(aName) > 1:
        sQuality = aName[1]
    elif aName:
        sQuality = aName[0]
    if sQuality == 'Torrentio':
        sQuality = ''

    sRelease = ''
    aTitleLines = [x.strip() for x in str(sTitle).split('\n') if x.strip()]
    if aTitleLines:
        sRelease = aTitleLines[0]

    sSeeds = ''
    oSeed = re.search(r'👤\s*([\d,.kK]+)', str(sTitle))
    if oSeed:
        sSeeds = oSeed.group(1)
    sSize = ''
    oSize = re.search(r'💾\s*([^\s]+)', str(sTitle))
    if oSize:
        sSize = oSize.group(1)
    sProvider = ''
    oProvider = re.search(r'⚙️\s*([^\s]+)', str(sTitle))
    if oProvider:
        sProvider = oProvider.group(1)

    sPlainName = sRelease or sQuality or 'Torrentio'
    sLabel = sPlainName
    aParts = []
    if sQuality:
        aParts.append('[COLOR yellow]%s[/COLOR]' % sQuality)
    aInfo = []
    if sSize:
        aInfo.append('Size: %s' % sSize)
    if sSeeds:
        aInfo.append('S:%s' % sSeeds)
    if sProvider:
        aInfo.append(sProvider)
    if aInfo:
        aParts.append('[COLOR grey]%s[/COLOR]' % ' | '.join(aInfo))
    if aParts:
        sLabel += ' ' + ' '.join(aParts)
    return sLabel, sPlainName


def __params(sTitle, sYear, sId, sType):
    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom')
    oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
    oOutputParameterHandler.addParameter('sImdbId', sId)
    oOutputParameterHandler.addParameter('sYear', sYear)
    oOutputParameterHandler.addParameter('sType', sType)
    return oOutputParameterHandler
