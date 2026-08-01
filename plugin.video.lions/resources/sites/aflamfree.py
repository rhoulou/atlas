# -*- coding: utf-8 -*-

import re
from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import VSlog, siteManager, addon

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/sites/logos/aflamfree.png'

SITE_IDENTIFIER = 'aflamfree'
SITE_NAME = 'Aflamfree'
SITE_DESC = 'arabic vod'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER).rstrip('/')

MOVIE_EN = (URL_MAIN + '/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D8%AC%D9%86%D8%A8%D9%8A%D8%A9', 'showLive')
MOVIE_ACTION = (URL_MAIN + '/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D8%AC%D9%86%D8%A8%D9%8A%D8%A9/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D9%84%D8%A3%D9%83%D8%B4%D9%86', 'showLive')
MOVIE_HORROR = (URL_MAIN + '/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D8%AC%D9%86%D8%A8%D9%8A%D8%A9/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D9%84%D8%B1%D8%B9%D8%A8', 'showLive')
MOVIE_ROMANCE = (URL_MAIN + '/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D8%AC%D9%86%D8%A8%D9%8A%D8%A9/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D9%84%D8%B1%D9%88%D9%85%D8%A7%D9%86%D8%B3%D9%8A%D8%A9', 'showLive')
MOVIE_COMEDY = (URL_MAIN + '/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D8%AC%D9%86%D8%A8%D9%8A%D8%A9/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D9%84%D9%83%D9%88%D9%85%D9%8A%D8%AF%D9%8A%D8%A7', 'showLive')
MOVIE_CRIME = (URL_MAIN + '/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D8%AC%D9%86%D8%A8%D9%8A%D8%A9/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D9%84%D8%AC%D8%B1%D9%8A%D9%85%D8%A9', 'showLive')
MOVIE_THRILLER = (URL_MAIN + '/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D8%AC%D9%86%D8%A8%D9%8A%D8%A9/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D9%84%D8%A5%D8%AB%D8%A7%D8%B1%D8%A9', 'showLive')
MOVIE_ADVENTURE = (URL_MAIN + '/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D8%AC%D9%86%D8%A8%D9%8A%D8%A9/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D9%84%D9%85%D8%BA%D8%A7%D9%85%D8%B1%D8%A7%D8%AA', 'showLive')
MOVIE_DRAMA = (URL_MAIN + '/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D8%AC%D9%86%D8%A8%D9%8A%D8%A9/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D9%84%D8%AF%D8%B1%D8%A7%D9%85%D8%A7', 'showLive')
MOVIE_INDIAN = (URL_MAIN + '/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D9%87%D9%86%D8%AF%D9%8A%D9%87', 'showLive')
MOVIE_ADULT = (URL_MAIN + '/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D8%AC%D9%86%D8%A8%D9%8A%D8%A9/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D9%84%D9%84%D9%83%D8%A8%D8%A7%D8%B1-%D9%81%D9%82%D8%B7', 'showLive')
MOVIE_TURKISH = (URL_MAIN + '/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%AA%D8%B1%D9%83%D9%8A%D8%A9', 'showLive')
MOVIE_ASIAN = (URL_MAIN + '/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D8%B3%D9%8A%D9%88%D9%8A%D8%A9', 'showLive')
MOVIE_CARTOON = (URL_MAIN + '/category/%D9%83%D8%A7%D8%B1%D8%AA%D9%88%D9%86-%D9%88%D8%A7%D9%86%D9%85%D9%8A', 'showLive')
MOVIE_RECENT = (URL_MAIN + '/recent', 'showLive')

URL_SEARCH = (URL_MAIN + '/?s=', 'showMoviesearch')
URL_SEARCH_MOVIES = (URL_MAIN + '/?s=', 'showMoviesearch')
FUNCTION_SEARCH = 'showMoviesearch'

def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_SEARCH[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search Movies', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_EN[0])
    oGui.addDir(SITE_IDENTIFIER, 'showLive', 'افلام اجنبية', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_ACTION[0])
    oGui.addDir(SITE_IDENTIFIER, 'showLive', 'افلام الأكشن', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_HORROR[0])
    oGui.addDir(SITE_IDENTIFIER, 'showLive', 'افلام الرعب', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_ROMANCE[0])
    oGui.addDir(SITE_IDENTIFIER, 'showLive', 'افلام الرومانسية', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_COMEDY[0])
    oGui.addDir(SITE_IDENTIFIER, 'showLive', 'افلام الكوميديا', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_CRIME[0])
    oGui.addDir(SITE_IDENTIFIER, 'showLive', 'افلام الجريمة', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_THRILLER[0])
    oGui.addDir(SITE_IDENTIFIER, 'showLive', 'افلام الإثارة', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_ADVENTURE[0])
    oGui.addDir(SITE_IDENTIFIER, 'showLive', 'افلام المغامرات', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_DRAMA[0])
    oGui.addDir(SITE_IDENTIFIER, 'showLive', 'افلام الدراما', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_INDIAN[0])
    oGui.addDir(SITE_IDENTIFIER, 'showLive', 'افلام هندية', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_ADULT[0])
    oGui.addDir(SITE_IDENTIFIER, 'showLive', 'افلام للكبار فقط', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_TURKISH[0])
    oGui.addDir(SITE_IDENTIFIER, 'showLive', 'افلام تركية', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_ASIAN[0])
    oGui.addDir(SITE_IDENTIFIER, 'showLive', 'افلام اسيوية', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_CARTOON[0])
    oGui.addDir(SITE_IDENTIFIER, 'showLive', 'كارتون وانمي', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_RECENT[0])
    oGui.addDir(SITE_IDENTIFIER, 'showLive', 'المضاف حديثا', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = URL_MAIN + '/?s=' + sSearchText
        showMoviesearch(sUrl)
        oGui.setEndOfDirectory()
        return

def showMoviesearch(sSearch=''):
    oGui = cGui()
    oParser = cParser()
    if sSearch:
        sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = '<a href="([^"]+)"[^>]*class="recent--block">\s*<div class="Poster">\s*<img[^>]*data-src="([^"]+)"[^>]*alt="([^"]*)"'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sTitle = aEntry[2].replace("مشاهدة", "").replace("فيلم", "").replace(" مترجم اون لاين وتحميل", "").replace(" مترجم اون لاين و تحميل", "").replace("اون لاين", "").replace("مترجم", "")
            siteUrl = aEntry[0]
            sThumb = aEntry[1]
            sYear = ''
            m = re.search(r'([1-2][0-9]{3})', sTitle)
            if m:
                sYear = str(m.group(0))
                sTitle = sTitle.replace(sYear, '')
            sDesc = ''

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', siteUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('sYear', sYear)
            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

        sNextPage = __checkForNextPage(sHtmlContent)
        if sNextPage:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showMoviesearch', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    if not sSearch:
        oGui.setEndOfDirectory()

def showLive():
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = '<a href="([^"]+)"[^>]*class="recent--block">\s*<div class="Poster">\s*<img[^>]*data-src="([^"]+)"[^>]*alt="([^"]*)"'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sTitle = aEntry[2].replace("مشاهدة", "").replace("فيلم", "").replace(" مترجم اون لاين وتحميل", "").replace(" مترجم اون لاين و تحميل", "").replace("اون لاين", "").replace("مترجم", "")
            siteUrl = aEntry[0]
            sThumb = aEntry[1]
            sYear = ''
            m = re.search(r'([1-2][0-9]{3})', sTitle)
            if m:
                sYear = str(m.group(0))
                sTitle = sTitle.replace(sYear, '')
            sDesc = ''

            oOutputParameterHandler.addParameter('siteUrl', siteUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

    sNextPage = __checkForNextPage(sHtmlContent)
    if sNextPage:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sNextPage)
        oGui.addDir(SITE_IDENTIFIER, 'showLive', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showHosters():
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    if '?watch=1' not in sUrl:
        sUrl = sUrl + '?watch=1'

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = r'data-watch="([^"]+)"[^>]*>.*?<span id="serverName">([^<]+)</span>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        for aEntry in aResult[1]:
            sHosterUrl = aEntry[0]
            sServerName = aEntry[1]
            if sHosterUrl.startswith('//'):
                sHosterUrl = 'https:' + sHosterUrl

            oHoster = None

            try:
                import resolveurl
                hmf = resolveurl.HostedMediaFile(url=sHosterUrl)
                if hmf.valid_url():
                    oHoster = cHosterGui().getHoster('resolver')
                    RH = sHosterUrl.split('/')[2].replace('www.', '').split('.')[0].upper()
                    oHoster.setRealHost(RH)
            except Exception:
                pass

            if not oHoster:
                oHoster = cHosterGui().checkHoster(sHosterUrl)

            if oHoster:
                sTitle = '%s [COLOR coral](%s)[/COLOR]' % (sMovieTitle, sServerName)
                oHoster.setDisplayName(sTitle)
                oHoster.setFileName(sMovieTitle)
                cHosterGui().showHoster(oGui, oHoster, sHosterUrl + "|verifypeer=false&Referer=" + URL_MAIN + "/", sThumb)

    oGui.setEndOfDirectory()

def __checkForNextPage(sHtmlContent):
    sPattern = 'class="page-numbers" href="([^"]+)"'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        return aResult[1][0]
    return False
