import re

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.comaddon import VSlog, siteManager, addon
from resources.lib.parser import cParser
from bs4 import BeautifulSoup
import resolveurl

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/shooflive_net.png'

SITE_IDENTIFIER = 'shooflive_net'
SITE_NAME = 'Shooflive'
SITE_DESC = 'arabic vod'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

MOVIE_FOREIGN = (URL_MAIN + '/foreign-movies/', 'showMovies')
MOVIE_TURKISH = (URL_MAIN + '/turkish-movies/', 'showMovies')
MOVIE_ARABIC = (URL_MAIN + '/arabic-movies/', 'showMovies')
MOVIE_ASIAN = (URL_MAIN + '/asian-movies/', 'showMovies')
MOVIE_INDIAN = (URL_MAIN + '/indian-movies/', 'showMovies')
MOVIE_ANIMATION = (URL_MAIN + '/animation-movies/', 'showMovies')

SERIE_ARABIC = (URL_MAIN + '/arabic-series/', 'showSeries')
SERIE_TURKISH = (URL_MAIN + '/turkish-series/', 'showSeries')
SERIE_FOREIGN = (URL_MAIN + '/foreign-series/', 'showSeries')
SERIE_ASIAN = (URL_MAIN + '/asian-series/', 'showSeries')
SERIE_DUBBED = (URL_MAIN + '/dubbed-series/', 'showSeries')
SERIE_RAMADAN = (URL_MAIN + '/ramadan-series-2026/', 'showSeries')

URL_SEARCH = (URL_MAIN + '/?s=', 'showSearch')
FUNCTION_SEARCH = 'showSearch'

def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'SEARCH', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIE_ARABIC[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات عربية', icons + '/Arabic.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIE_TURKISH[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات تركية', icons + '/Turkish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIE_FOREIGN[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات اجنبية', icons + '/TVShowsEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIE_ASIAN[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات اسيوية', icons + '/Asian.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIE_DUBBED[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات مدبلجة', icons + '/Arabic.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', SERIE_RAMADAN[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات رمضان 2026', icons + '/Ramadan.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_FOREIGN[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام اجنبية', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_TURKISH[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام تركية', icons + '/Turkish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_ARABIC[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام عربية', icons + '/Arabic.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_ASIAN[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام اسيوية', icons + '/Asian.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_INDIAN[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام هندية', icons + '/Hindi.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_ANIMATION[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام انيميشن', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showSearch():
    oGui = cGui()

    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = URL_MAIN + '/?s=' + sSearchText
        _listItems(sUrl, oGui)
        oGui.setEndOfDirectory()
        return

def showMovies(sSearch=''):
    oGui = cGui()
    if sSearch:
        sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    _listItems(sUrl, oGui, isSeries=False)

    if not sSearch:
        _checkNextPage(sUrl, oGui, 'showMovies')
        oGui.setEndOfDirectory()

def showSeries(sSearch=''):
    oGui = cGui()
    if sSearch:
        sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    _listItems(sUrl, oGui, isSeries=True)

    if not sSearch:
        _checkNextPage(sUrl, oGui, 'showSeries')
        oGui.setEndOfDirectory()

def showEpisodes():
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = '<div class="block-post">\s*<a href="([^"]+)" title="[^"]*">(?:[\s\S]*?<img[^>]+data-src=([^\s>]+)[^>]*>)?[\s\S]*?<div class="title">([^<]+)</div>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            siteUrl = aEntry[0]
            sThumb = aEntry[1] if aEntry[1] else sThumb
            sTitle = aEntry[2].strip()

            oOutputParameterHandler.addParameter('siteUrl', siteUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            oGui.addEpisode(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, '', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showHosters():
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    soup = BeautifulSoup(sHtmlContent, "html.parser")
    watch = soup.select_one('.watch iframe')
    if not watch or not watch.get('src'):
        oGui.setEndOfDirectory()
        return

    sDilayUrl = watch['src']
    if sDilayUrl.startswith('//'):
        sDilayUrl = 'https:' + sDilayUrl

    oRequestHandler = cRequestHandler(sDilayUrl)
    sAlbaHtml = oRequestHandler.request()

    soup = BeautifulSoup(sAlbaHtml, "html.parser")
    servers = soup.select('.aplr-menu a.aplr-link')
    if not servers:
        oGui.setEndOfDirectory()
        return

    for server in servers:
        try:
            sServerUrl = server.get('href')
            sServerName = server.get_text(strip=True)
            if not sServerUrl:
                continue

            oReq = cRequestHandler(sServerUrl)
            sServerHtml = oReq.request()

            serverSoup = BeautifulSoup(sServerHtml, "html.parser")
            iframe = serverSoup.select_one('.video-con iframe')
            if not iframe or not iframe.get('src'):
                continue

            sEmbedUrl = iframe['src']
            sMediaUrl = sEmbedUrl

            hmf = resolveurl.HostedMediaFile(url=sEmbedUrl)
            if hmf.valid_url():
                oHoster = cHosterGui().getHoster('resolver')
            else:
                oHoster = cHosterGui().checkHoster(sEmbedUrl)

            if not oHoster:
                try:
                    oReq = cRequestHandler(sEmbedUrl)
                    sEmbedHtml = oReq.request()
                    aMatch = re.search(r'sources:\s*\[{file:"([^"]+)"', sEmbedHtml, re.IGNORECASE)
                    if aMatch:
                        sMediaUrl = aMatch.group(1) + '|Referer=' + sEmbedUrl
                        oHoster = cHosterGui().getHoster('lien_direct')
                except Exception:
                    pass

            if oHoster:
                oHoster.setDisplayName(f'{sMovieTitle} [{sServerName}]')
                oHoster.setFileName(sMovieTitle)
                cHosterGui().showHoster(oGui, oHoster, sMediaUrl, sThumb)
        except Exception as e:
            VSlog('shooflive_net showHosters: ' + str(e))

    oGui.setEndOfDirectory()

def _listItems(sUrl, oGui, isSeries=False):
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = '<div class="block-post">\s*<a href="([^"]+)" title="[^"]*">(?:[\s\S]*?<img[^>]+data-src=([^\s>]+)[^>]*>)?[\s\S]*?<div class="title">([^<]+)</div>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            siteUrl = aEntry[0]
            sThumb = aEntry[1]
            sTitle = aEntry[2].strip()

            if isSeries:
                oOutputParameterHandler.addParameter('siteUrl', siteUrl)
                oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
                oOutputParameterHandler.addParameter('sThumb', sThumb)

                oGui.addTV(SITE_IDENTIFIER, 'showEpisodes', sTitle, '', sThumb, '', oOutputParameterHandler)
            else:
                oOutputParameterHandler.addParameter('siteUrl', siteUrl)
                oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
                oOutputParameterHandler.addParameter('sThumb', sThumb)

                oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, '', oOutputParameterHandler)

def _checkNextPage(sUrl, oGui, sFunc):
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = "<a href='([^']+)' class='inactive'[^>]*>(\d+)</a>"
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sNextUrl = aEntry[0]
            sPage = aEntry[1]
            if sNextUrl != sUrl:
                oOutputParameterHandler.addParameter('siteUrl', sNextUrl)
                oGui.addDir(SITE_IDENTIFIER, sFunc, '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)
                break
