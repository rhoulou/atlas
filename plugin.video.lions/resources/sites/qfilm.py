# -*- coding: utf-8 -*-

import re
import json
import urllib.request
import urllib.parse
import ssl

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.comaddon import progress, VSlog, siteManager, addon
from resources.lib.parser import cParser

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/sites/logos/qfilm.png'

SITE_IDENTIFIER = 'qfilm'
SITE_NAME = 'Q-Film'
SITE_DESC = 'arabic vod'

UA = 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.48 Mobile Safari/537.36'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

MOVIE_EN = (URL_MAIN + 'category.php?cat=english-movies', 'showMovies')
MOVIE_AR = (URL_MAIN + 'category.php?cat=arabic-movies', 'showMovies')
MOVIE_TURK = (URL_MAIN + 'category.php?cat=turkish-movies', 'showMovies')
MOVIE_HI = (URL_MAIN + 'category.php?cat=indian-movies', 'showMovies')
MOVIE_ASIAN = (URL_MAIN + 'category.php?cat=asian-movies', 'showMovies')
ANIM_MOVIES = (URL_MAIN + 'category.php?cat=anime-movies', 'showMovies')
MOVIE_DUBBED = (URL_MAIN + 'category.php?cat=dubbed-movies', 'showMovies')
MOVIE_2026 = (URL_MAIN + 'category.php?cat=2026-movies', 'showMovies')
MOVIE_GENRES = (True, 'moviesGenres')

URL_SEARCH = (URL_MAIN + 'search.php?keywords=', 'showMovies')
URL_SEARCH_MOVIES = (URL_MAIN + 'search.php?keywords=', 'showMovies')
FUNCTION_SEARCH = 'showSearch'


def _fetch(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    resp = urllib.request.urlopen(req, context=ctx, timeout=30)
    data = resp.read()
    if resp.headers.get('Content-Encoding') == 'gzip':
        import gzip
        data = gzip.decompress(data)
    return data.decode('utf-8', errors='replace')


def _fixSslUrl(url):
    if url and url.startswith('https://'):
        url = 'http://' + url[8:]
    return url


def _searchKeywords(sUrl):
    oMatch = re.search(r'keywords=([^&\s]+)', sUrl)
    if not oMatch:
        return []
    sQuery = urllib.parse.unquote_plus(oMatch.group(1))
    return [w.lower() for w in sQuery.split() if not re.match(r'^\d{4}$', w)]


def _matchesSearch(sTitle, aKeywords):
    if not aKeywords:
        return True
    sTitleLower = sTitle.lower()
    return all(w in sTitleLower for w in aKeywords)


def load():
    oGui = cGui()
    addons = addon()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_SEARCH[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', addons.VSlang(30078), LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_2026[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام 2026', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_EN[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام أجنبية', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_AR[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام عربية', icons + '/Arabic.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_HI[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام هندية', icons + '/Hindi.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_TURK[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام تركية', icons + '/Turkish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_ASIAN[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام آسيوية', icons + '/Asian.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', ANIM_MOVIES[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام انيميشن', icons + '/Cartoon.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_DUBBED[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام مدبلجة', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_GENRES[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_GENRES[1], 'الأفلام (الأنواع)', icons + '/All.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = URL_MAIN + 'search.php?keywords=' + urllib.parse.quote(sSearchText)
        showMovies(sUrl)
        oGui.setEndOfDirectory()
        return


def moviesGenres():
    oGui = cGui()

    liste = []
    liste.append(['اكشن', URL_MAIN + 'category.php?cat=action-movies'])
    liste.append(['انيميشن', URL_MAIN + 'category.php?cat=anime-movies'])
    liste.append(['مغامرات', URL_MAIN + 'category.php?cat=adventure-movies'])
    liste.append(['غموض', URL_MAIN + 'category.php?cat=mystery-movies'])
    liste.append(['تاريخي', URL_MAIN + 'category.php?cat=historical-movies'])
    liste.append(['كوميديا', URL_MAIN + 'category.php?cat=comedy-movies'])
    liste.append(['موسيقى', URL_MAIN + 'category.php?cat=musical-movies'])
    liste.append(['سيرة ذاتية', URL_MAIN + 'category.php?cat=biography-movies'])
    liste.append(['دراما', URL_MAIN + 'category.php?cat=drama-movies'])
    liste.append(['رعب', URL_MAIN + 'category.php?cat=horror-movies'])
    liste.append(['عائلى', URL_MAIN + 'category.php?cat=family-movies'])
    liste.append(['فانتازيا', URL_MAIN + 'category.php?cat=fantasy-movies'])
    liste.append(['حروب', URL_MAIN + 'category.php?cat=war-movies'])
    liste.append(['الجريمة', URL_MAIN + 'category.php?cat=crime-movies'])
    liste.append(['رومانسى', URL_MAIN + 'category.php?cat=romance-movies'])
    liste.append(['خيال علمى', URL_MAIN + 'category.php?cat=sci-fi-movies'])
    liste.append(['اثارة', URL_MAIN + 'category.php?cat=thriller-movies'])
    liste.append(['وثائقى', URL_MAIN + 'category.php?cat=documentary-movies'])

    for sTitle, sUrl in liste:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oGui.addDir(SITE_IDENTIFIER, 'showMovies', sTitle, 'genres.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showMovies(sSearch=''):
    oGui = cGui()
    if sSearch:
        sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    sHtmlContent = _fetch(sUrl)
    sHtmlContent = sHtmlContent.replace('\r', '').replace('\n', '')

    sPattern = '<div class="thumbnail">.*?<a href="([^"]+)"[^>]*title="([^"]*)".*?data-echo="([^"]+)"'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    aKeywords = _searchKeywords(sUrl)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sTitle = aEntry[1].replace("مشاهدة", "").replace("كامل", "").replace("مشاهده", "")
            sTitle = sTitle.replace("مترجم", "").replace("فيلم", "").replace("اونلاين", "")
            sTitle = sTitle.replace("اون لاين", "").replace("برنامج", "")
            sTitle = sTitle.replace("HD", "").replace("WEB-DL", "").replace("BRRip", "")
            sTitle = sTitle.replace("720p", "").replace("1080p", "").replace("4K", "")
            sTitle = sTitle.replace("BluRay", "").replace("HDRip", "").replace("DVDRip", "")
            sTitle = sTitle.replace("WEBRip", "").replace("HDTV", "").replace("BDRip", "")
            sTitle = sTitle.replace("HDCAM", "").replace("HDTC", "").replace("HC", "")
            sTitle = sTitle.replace("Full HD", "").replace("انمي", "").strip()
            if not _matchesSearch(sTitle, aKeywords):
                continue

            sUrl2 = aEntry[0]
            sThumb = _fixSslUrl(aEntry[2])
            sDesc = ''
            sYear = ''
            m = re.search(r'([0-9]{4})', sTitle)
            if m:
                sYear = str(m.group(0))
                sTitle = sTitle.replace(sYear, '')

            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('sYear', sYear)
            oOutputParameterHandler.addParameter('sDesc', sDesc)

            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

        sNextPage = __checkForNextPage(sHtmlContent, sUrl)
        if sNextPage:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Next >>>[/COLOR]', 'next.png', oOutputParameterHandler)

    if not sSearch:
        oGui.setEndOfDirectory()


def __checkForNextPage(sHtmlContent, sCurrentUrl):
    sPattern = r'<li class>\s*<a href="([^"]*\?[^"]*page=\d+)"'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        sNext = aResult[1][0]
        if not sNext.startswith('http'):
            sNext = URL_MAIN + sNext
        return sNext
    return False


def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    m = re.search(r'vid=([^&]+)', sUrl)
    if not m:
        oGui.setEndOfDirectory()
        return

    vid = m.group(1)
    sPlayUrl = URL_MAIN + 'play.php?vid=' + vid

    try:
        sHtmlContent = _fetch(sPlayUrl)
    except Exception as e:
        VSlog('qfilm play.php error: ' + str(e))
        oGui.setEndOfDirectory()
        return

    sHtmlContent = sHtmlContent.replace('\r', '').replace('\n', ' ')

    aHosterUrls = []

    sPattern = r'var servers\s*=\s*\[(.*?)\]'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        serversRaw = aResult[1][0].replace('\\', '')
        srcMatches = re.findall(r'src="([^"]+)"', serversRaw)
        for src in srcMatches:
            if src.startswith('//'):
                src = 'https:' + src
            aHosterUrls.append(src)

    if not aHosterUrls:
        sPattern2 = r'<div class="embed_server">\s*<iframe[^>]+src="([^"]+)"'
        aResult2 = oParser.parse(sHtmlContent, sPattern2)
        if aResult2[0]:
            for src in aResult2[1]:
                if src.startswith('//'):
                    src = 'https:' + src
                aHosterUrls.append(src)

    if aHosterUrls:
        seen = set()
        for sHosterUrl in aHosterUrls:
            if sHosterUrl in seen:
                continue
            seen.add(sHosterUrl)

            sDirectUrl = _extractVideoFromEmbed(sHosterUrl)
            if sDirectUrl:
                referer = sHosterUrl.split('/e/')[0] + '/' if '/e/' in sHosterUrl else sHosterUrl
                sDirectUrl = sDirectUrl + '|Referer=' + urllib.parse.quote(referer) + '&User-Agent=' + urllib.parse.quote(UA)
                oHoster = cHosterGui().getHoster('lien_direct')
                if oHoster:
                    oHoster.setDisplayName(sMovieTitle)
                    oHoster.setFileName(sMovieTitle)
                    cHosterGui().showHoster(oGui, oHoster, sDirectUrl, sThumb)
            else:
                oHoster = cHosterGui().checkHoster(sHosterUrl)
                if oHoster:
                    oHoster.setDisplayName(sMovieTitle)
                    oHoster.setFileName(sMovieTitle)
                    cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)

    oGui.setEndOfDirectory()


def _extractVideoFromEmbed(sEmbedUrl):
    try:
        sEmbedHtml = _fetch(sEmbedUrl)
    except Exception:
        return False

    sEmbedHtml = sEmbedHtml.replace('\r', '').replace('\n', ' ').replace('\\/', '/')

    m = re.search(r'file\s*:\s*"([^"]+\.m3u8[^"]*)"', sEmbedHtml)
    if m:
        return m.group(1)

    m = re.search(r'file\s*:\s*"([^"]+\.mp4[^"]*)"', sEmbedHtml)
    if m:
        return m.group(1)

    m = re.search(r'sources\s*:\s*\[\s*\{\s*file\s*:\s*"([^"]+)"', sEmbedHtml)
    if m:
        return m.group(1)

    m = re.search(r'file\s*:\s*"([^"]+)"', sEmbedHtml)
    if m:
        return m.group(1)

    return False
