# -*- coding: utf-8 -*-

import re

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import siteManager, addon

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/sites/logos/moviegate.png'

SITE_IDENTIFIER = 'moviegate'
SITE_NAME = 'Moviegate'
SITE_DESC = 'arabic vod'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER).rstrip('/')

MOVIE_EN = (URL_MAIN + '/category/movis/all-movies/', 'showMovies')
MOVIE_ASIAN = (URL_MAIN + '/category/movis/asian-movies/', 'showMovies')
MOVIE_TURKISH = (URL_MAIN + '/category/movis/turkish-movies/', 'showMovies')
MOVIE_FRENCH = (URL_MAIN + '/category/movis/french-movies/', 'showMovies')
MOVIE_DUBBED = (URL_MAIN + '/category/movis/dubbed-movies/', 'showMovies')
MOVIE_INDIAN = (URL_MAIN + '/category/movis/indian-movies/', 'showMovies')
MOVIE_CARTOON = (URL_MAIN + '/category/cartoon-animation/', 'showMovies')
MOVIE_RECENT = (URL_MAIN + '/recent/', 'showMovies')

GENRE_ACTION = (URL_MAIN + '/genre/action/', 'showMovies')
GENRE_HORROR = (URL_MAIN + '/genre/horror/', 'showMovies')
GENRE_SCIFI = (URL_MAIN + '/genre/science-fiction/', 'showMovies')
GENRE_FANTASY = (URL_MAIN + '/genre/fantasy-movies/', 'showMovies')
GENRE_ROMANCE = (URL_MAIN + '/genre/romantic/', 'showMovies')
GENRE_COMEDY = (URL_MAIN + '/genre/comedy/', 'showMovies')
GENRE_THRILLER = (URL_MAIN + '/genre/thrilling/', 'showMovies')
GENRE_CRIME = (URL_MAIN + '/genre/crime/', 'showMovies')
GENRE_ADVENTURE = (URL_MAIN + '/genre/adventure/', 'showMovies')
GENRE_DRAMA = (URL_MAIN + '/genre/drama/', 'showMovies')
GENRE_MYSTERY = (URL_MAIN + '/genre/mystery/', 'showMovies')
GENRE_FAMILY = (URL_MAIN + '/genre/family/', 'showMovies')
GENRE_HISTORY = (URL_MAIN + '/genre/historic/', 'showMovies')
GENRE_WESTERN = (URL_MAIN + '/genre/western/', 'showMovies')

TAG_CLASSIC = (URL_MAIN + '/tag/classic-movies/', 'showMovies')
TAG_TELUGU = (URL_MAIN + '/tag/telugu/', 'showMovies')
TAG_TAMIL = (URL_MAIN + '/tag/tamil-movies/', 'showMovies')
TAG_MALAYALAM = (URL_MAIN + '/tag/malayalam-movies/', 'showMovies')
TAG_KANNADA = (URL_MAIN + '/tag/%d8%a7%d9%81%d9%84%d8%a7%d9%85-%d9%83%d9%86%d8%a7%d8%af%d9%8a%d8%a9/', 'showMovies')
TAG_PUNJABI = (URL_MAIN + '/tag/punjabi/', 'showMovies')
TAG_MARATHI = (URL_MAIN + '/tag/%d8%a7%d9%81%d9%84%d8%a7%d9%85-%d9%85%d8%a7%d8%b1%d8%a7%d8%ab%d9%8a%d8%a9/', 'showMovies')
TAG_BENGALI = (URL_MAIN + '/tag/%d8%a7%d9%81%d9%84%d8%a7%d9%85-%d8%a8%d9%86%d8%ba%d8%a7%d9%84%d9%8a%d8%a9/', 'showMovies')
TAG_GUJARATI = (URL_MAIN + '/tag/%d8%a7%d9%81%d9%84%d8%a7%d9%85-%d9%83%d8%ac%d8%b1%d8%a7%d8%aa%d9%8a%d8%a9/', 'showMovies')

LANG_KOREAN = (URL_MAIN + '/language/%d8%a7%d9%84%d9%83%d9%88%d8%b1%d9%8a%d8%a9/', 'showMovies')
LANG_JAPANESE = (URL_MAIN + '/language/%d8%a7%d9%84%d9%8a%d8%a7%d8%a8%d8%a7%d9%86%d9%8a%d8%a9/', 'showMovies')
LANG_CHINESE = (URL_MAIN + '/language/chinese/', 'showMovies')
LANG_THAI = (URL_MAIN + '/language/%d8%a7%d9%84%d8%aa%d8%a7%d9%8a%d9%84%d8%a7%d9%86%d8%af%d9%8a%d8%a9/', 'showMovies')
LANG_INDONESIAN = (URL_MAIN + '/language/%d8%a7%d9%84%d8%a7%d9%86%d8%af%d9%88%d9%86%d9%8a%d8%b3%d9%8a%d8%a9/', 'showMovies')
LANG_FILIPINO = (URL_MAIN + '/language/%d8%a7%d9%84%d9%81%d9%84%d8%a8%d9%8a%d9%86%d9%8a%d8%a9/', 'showMovies')
LANG_MONGOLIAN = (URL_MAIN + '/language/%d8%a7%d9%84%d9%85%d9%86%d8%ba%d9%88%d9%84%d9%8a%d8%a9/', 'showMovies')

URL_SEARCH = (URL_MAIN + '/?s=', 'showMovies')
URL_SEARCH_MOVIES = (URL_MAIN + '/?s=', 'showMovies')
FUNCTION_SEARCH = 'showMovies'


def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_SEARCH[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_EN[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام اجنبية', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_ASIAN[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام اسيوية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_TURKISH[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام تركية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_FRENCH[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام فرنسية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_DUBBED[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام مدبلجة', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_INDIAN[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام هندية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_CARTOON[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'كارتون وانيميشن', icons + '/Anime.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', GENRE_ACTION[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام الأكشن', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', GENRE_HORROR[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام الرعب', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', GENRE_SCIFI[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام الخيال العلمي', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', GENRE_FANTASY[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام الفانتازيا', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', GENRE_ROMANCE[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام رومانسية', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', GENRE_COMEDY[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام الكوميديا', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', GENRE_THRILLER[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام الإثارة والتشويق', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', GENRE_CRIME[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام الجريمة', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', GENRE_ADVENTURE[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام المغامرات', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', GENRE_DRAMA[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام الدراما', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', GENRE_MYSTERY[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام الغموض', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', GENRE_FAMILY[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام عائلية', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', GENRE_HISTORY[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام تاريخية', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', GENRE_WESTERN[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام ويسترن', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', TAG_CLASSIC[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام كلاسيكية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', TAG_TELUGU[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام التيلجو', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', TAG_TAMIL[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام تاميلية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', TAG_MALAYALAM[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام ماليالامية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', TAG_KANNADA[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام كنادية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', TAG_PUNJABI[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام بنجابية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', TAG_MARATHI[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام ماراثية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', TAG_BENGALI[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام بنغالية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', TAG_GUJARATI[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام كجراتية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', LANG_KOREAN[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام كورية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', LANG_JAPANESE[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام يابانية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', LANG_CHINESE[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام صينية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', LANG_THAI[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام تايلاندية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', LANG_INDONESIAN[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام إندونيسية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', LANG_FILIPINO[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام فلبينية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', LANG_MONGOLIAN[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام منغولية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_RECENT[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'المضاف حديثا', LOGO, oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = URL_MAIN + '/?s=' + sSearchText
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
    sPattern = r'<a href="([^"]+)"[^>]*title="([^"]+)"[^>]*class="recent--block"[^>]*>.*?data-src="([^"]+)"'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sUrl2 = aEntry[0]
            sTitle = aEntry[1].strip()
            sThumb = aEntry[2]

            sTitle = sTitle.replace('مشاهدة', '').replace('انمي', '').replace('مترجمة', '').replace('مترجم', '').replace('اونلاين', '').replace('مباشرة', '').replace('جودة عالية', '').replace('اون لاين', '').replace(' HD', '').strip()

            sYear = ''
            m = re.search(r'(\d{4})', sTitle)
            if m:
                sYear = m.group(1)

            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('sYear', sYear)

            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, '', oOutputParameterHandler)

    if not sSearch:
        sNextPage = __checkForNextPage(sHtmlContent)
        if sNextPage:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)
        oGui.setEndOfDirectory()


def showHosters():
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    if not sUrl.endswith('/watch/') and '/watch' not in sUrl:
        if sUrl.endswith('/'):
            sUrl = sUrl + 'watch/'
        else:
            sUrl = sUrl + '/watch/'

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    oParser = cParser()
    servers = []

    sPattern = r'data-watch="([^"]+)"'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        for aEntry in aResult[1]:
            sHosterUrl = aEntry
            if sHosterUrl.startswith('//'):
                sHosterUrl = 'https:' + sHosterUrl
            if sHosterUrl not in servers:
                servers.append(sHosterUrl)

    for sHosterUrl in servers:
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

        if not oHoster:
            oHoster = cHosterGui().getHoster('lien_direct')

        if oHoster:
            oHoster.setDisplayName(sMovieTitle)
            oHoster.setFileName(sMovieTitle)
            cHosterGui().showHoster(oGui, oHoster, sHosterUrl + '|verifypeer=false&Referer=' + URL_MAIN + '/', sThumb)

    oGui.setEndOfDirectory()


def __checkForNextPage(sHtmlContent):
    oParser = cParser()
    sPattern = r'class="page-numbers" href="([^"]+)"'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        return aResult[1][0]
    return False
