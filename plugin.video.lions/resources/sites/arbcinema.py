# -*- coding: utf-8 -*-
# zombi https://github.com/zombiB/zombi-addons/

import re
import base64

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import siteManager, addon

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/sites/logos/arbcinema.png'

SITE_IDENTIFIER = 'arbcinema'
SITE_NAME = 'Arbcinema'
SITE_DESC = 'arabic vod'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER).rstrip('/')

URL_SEARCH = (URL_MAIN + '/browse.php?search=', 'showMovies')
URL_SEARCH_MOVIES = (URL_MAIN + '/browse.php?search=', 'showMovies')
FUNCTION_SEARCH = 'showMovies'

def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=arabic-movies')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام عربية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=foreign-movies')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام أجنبية', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=asian&type=movie')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام كورية', icons + '/Asian.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=indian&type=movie')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام هندية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=Turkish&type=movie')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام تركية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=anime')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أنمي', icons + '/Anime.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=dubbed&type=movie')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام مدبلجة', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=cartoon')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'كارتون', icons + '/Anime.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=classic')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'كلاسيكيات', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=arabic-series')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'مسلسلات عربية', icons + '/Series.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=foreign-series')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'مسلسلات أجنبية', icons + '/Series.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=asian&type=series')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'مسلسلات كورية', icons + '/Series.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=indian&type=series')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'مسلسلات هندية', icons + '/Series.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=Turkish&type=series')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'مسلسلات تركية', icons + '/Series.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=dubbed&type=series')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'مسلسلات مدبلجة', icons + '/Series.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=ramadan-2026')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'رمضان 2026', icons + '/Series.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=plays')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'مسرحيات', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=tv_shows')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'برامج TV', icons + '/Series.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=wrestling')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'مصارعة حرة', icons + '/Series.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/browse.php?category=historical')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'التاريخ والدين', LOGO, oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showSearch():
    oGui = cGui()

    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = URL_MAIN + '/browse.php?search=' + sSearchText
        showMovies(sUrl)
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
    sPattern = r'href="(/(?:movie|series)/[^"]+)"[\s\S]*?<img\s+src="([^"]+)"[\s\S]*?class="modern-title[^"]*">([^<]+)</h[23]>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        for aEntry in aResult[1]:
            sUrl2 = URL_MAIN + aEntry[0].replace('/movie/', '/watch/')
            sThumb = aEntry[1]
            if sThumb.startswith('/'):
                sThumb = URL_MAIN + sThumb
            sTitle = aEntry[2].strip()

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            if '/movie/' in aEntry[0]:
                oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, '', oOutputParameterHandler)
            else:
                oGui.addTV(SITE_IDENTIFIER, 'showEpisodes', sTitle, '', sThumb, '', oOutputParameterHandler)

        sNextPage = __checkForNextPage(sHtmlContent, sUrl)
        if sNextPage:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    if not sSearch:
        oGui.setEndOfDirectory()

def showEpisodes():
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    sEpisodesUrl = sUrl.replace('/series/', '/episodes/')
    oRequestHandler = cRequestHandler(sEpisodesUrl)
    sHtmlContent = oRequestHandler.request()

    oParser = cParser()
    sPattern = r'href="(/watch/[^"]*\?episode=(\d+))"'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        for aEntry in aResult[1]:
            sEpUrl = URL_MAIN + aEntry[0]
            sEpTitle = 'الحلقة ' + aEntry[1]

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sEpUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle + ' - ' + sEpTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            oGui.addEpisode(SITE_IDENTIFIER, 'showHosters', sEpTitle, '', sThumb, '', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showHosters():
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    oParser = cParser()
    servers = []

    sPattern = r'href="(https://cdn-streaming-fast\.com/hls/[^"]+)"[^>]*style="display:none'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        for aEntry in aResult[1]:
            sHosterUrl = aEntry + '|verifypeer=false'
            if sHosterUrl not in [s[1] for s in servers]:
                servers.append(('CDN Direct', sHosterUrl))

    sPattern = r"changeSecureServer\('([^']+)'\s*,\s*this\)\s*\"[^>]*>\s*<i[^>]*></i>\s*([^<]+)"
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        for aEntry in aResult[1]:
            try:
                sHosterUrl = base64.b64decode(aEntry[0]).decode('utf-8')[::-1]
                if sHosterUrl.startswith('//'):
                    sHosterUrl = 'https:' + sHosterUrl
                sServerName = aEntry[1].strip()
                sKey = sHosterUrl.split('|')[0]
                if sKey not in [s[1].split('|')[0] for s in servers]:
                    servers.append((sServerName, sHosterUrl))
            except Exception:
                pass

    sPattern = r'"embedUrl"\s*:\s*"([^"]+)"'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        for aEntry in aResult[1]:
            sHosterUrl = aEntry
            if sHosterUrl.startswith('//'):
                sHosterUrl = 'https:' + sHosterUrl
            sKey = sHosterUrl.split('|')[0]
            if sKey not in [s[1].split('|')[0] for s in servers]:
                servers.append(('Embed', sHosterUrl))

    for sServerName, sHosterUrl in servers:
        oHoster = None
        try:
            import resolveurl
            hmf = resolveurl.HostedMediaFile(url=sHosterUrl.split('|')[0])
            if hmf.valid_url():
                oHoster = cHosterGui().getHoster('resolver')
                RH = sHosterUrl.split('/')[2].replace('www.', '').split('.')[0].upper()
                oHoster.setRealHost(RH)
        except Exception:
            pass

        if not oHoster:
            oHoster = cHosterGui().checkHoster(sHosterUrl)

        if oHoster:
            if sServerName and sServerName != 'CDN Direct':
                sTitle = '%s [COLOR coral](%s)[/COLOR]' % (sMovieTitle, sServerName)
            else:
                sTitle = sMovieTitle
            oHoster.setDisplayName(sTitle)
            oHoster.setFileName(sMovieTitle)
            cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)

    oGui.setEndOfDirectory()

def __checkForNextPage(sHtmlContent, sCurrentUrl):
    oParser = cParser()
    sPattern = 'href="([^"]+)"[^>]*aria-label="Next"'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        sNext = aResult[1][0]
        if sNext.startswith('?'):
            sBase = sCurrentUrl.split('?')[0]
            return sBase + sNext
        return sNext

    return False
