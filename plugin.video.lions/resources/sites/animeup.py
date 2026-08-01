# -*- coding: utf-8 -*-
# zombi https://github.com/zombiB/zombi-addons/

import re

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.comaddon import VSlog, siteManager, addon
from resources.lib.parser import cParser

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/sites/logos/animeup.png'

SITE_IDENTIFIER = 'animeup'
SITE_NAME = 'Anime4up'
SITE_DESC = 'arabic vod'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER).rstrip('/')

ANIM_NEWS = (URL_MAIN + '/anime-type/tv2/', 'showSeries')
ANIM_MOVIES = (URL_MAIN + '/anime-type/movie-3/', 'showMovies')
ANIM_SUB = (URL_MAIN + '/anime-category/%D8%A7%D9%84%D8%A3%D9%86%D9%85%D9%8A-%D8%A7%D9%84%D9%85%D8%AA%D8%B1%D8%AC%D9%85/', 'showSeries')
ANIM_DUBBED = (URL_MAIN + '/anime-category/%d8%a7%d9%84%d8%a7%d9%86%d9%85%d9%8a-%d8%a7%d9%84%d9%85%d8%af%d8%a8%d9%84%d8%ac/', 'showSeries')

URL_SEARCH = (URL_MAIN + '/?search_param=animes&s=', 'showMovies')
URL_SEARCH_MOVIES = (URL_MAIN + '/?search_param=animes&s=', 'showMovies')
URL_SEARCH_ANIMS = (URL_MAIN + '/?search_param=animes&s=', 'showSeries')
FUNCTION_SEARCH = 'showMovies'

def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'SEARCH_MOVIES', LOGO, oOutputParameterHandler)

    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSeriesSearch', 'SEARCH_SERIES', LOGO, oOutputParameterHandler)

    oOutputParameterHandler.addParameter('siteUrl', ANIM_MOVIES[0])
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'افلام الانمي', icons + '/Anime.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', ANIM_NEWS[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات إنمي', icons + '/Anime.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', ANIM_DUBBED[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'انمي مدبلج', icons + '/Dubbed.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', ANIM_SUB[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'انمي مترجم', icons + '/Subtitled.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showSearch():
    oGui = cGui()

    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = URL_MAIN + '/?search_param=animes&s=' + sSearchText
        showMovies(sUrl)
        oGui.setEndOfDirectory()
        return

def showSeriesSearch():
    oGui = cGui()

    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = URL_MAIN + '/?search_param=animes&s=' + sSearchText
        showSeries(sUrl)
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

    VSlog('[animeup] showMovies URL: %s' % sUrl)
    VSlog('[animeup] showMovies: response length %d' % (len(sHtmlContent) if sHtmlContent else 0))
    if sHtmlContent:
        VSlog('[animeup] showMovies: snippet: %s' % sHtmlContent[:300])

    oParser = cParser()
    sPattern = r'<img[^>]+data-image="([^"]+)"[^>]*>.*?<a[^>]+href="([^"]+)"[^>]*class="overlay"[^>]*>.*?<h3[^>]*>\s*<a[^>]+href="[^"]*"[^>]*>\s*([^<]+)</a>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    VSlog('[animeup] showMovies: found %d items' % (len(aResult[1]) if aResult[0] else 0))

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sThumb = aEntry[0]
            siteUrl = aEntry[1]
            sTitle = aEntry[2].strip()

            sTitle = sTitle.replace("مشاهدة", "").replace("مسلسل", "").replace("انمي", "").replace("مترجمة", "").replace("مترجم", "").replace("فيلم", "").replace("والأخيرة", "").replace("مدبلج للعربية", "مدبلج").replace("والاخيرة", "").replace("كاملة", "").replace("حلقات كاملة", "").replace("اونلاين", "").replace("مباشرة", "").replace("انتاج ", "").replace("جودة عالية", "").replace("كامل", "").replace("HD", "").replace("السلسلة الوثائقية", "").replace("الفيلم الوثائقي", "").replace("اون لاين", "").replace("مدبلج", "").replace("مدبلجة", "").replace("مدبلجه", "").replace("الفلم", "").replace("الفيلم", "").replace("فلم", "").replace("فيلم", "").replace("مسلسل", "").replace("للعربية", "")
            sTitle = sTitle.strip()

            sDesc = ''

            oOutputParameterHandler.addParameter('siteUrl', siteUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            oGui.addMovie(SITE_IDENTIFIER, 'showEpisodes', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

        sNextPage = __checkForNextPage(sHtmlContent)
        if sNextPage:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    if not sSearch:
        oGui.setEndOfDirectory()

def showSeries(sSearch=''):
    oGui = cGui()
    if sSearch:
        sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    VSlog('[animeup] showSeries URL: %s' % sUrl)
    VSlog('[animeup] showSeries: response length %d' % (len(sHtmlContent) if sHtmlContent else 0))
    if sHtmlContent:
        VSlog('[animeup] showSeries: snippet: %s' % sHtmlContent[:300])

    oParser = cParser()
    sPattern = r'<img[^>]+data-image="([^"]+)"[^>]*>.*?<a[^>]+href="([^"]+)"[^>]*class="overlay"[^>]*>.*?<h3[^>]*>\s*<a[^>]+href="[^"]*"[^>]*>\s*([^<]+)</a>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    VSlog('[animeup] showSeries: found %d items' % (len(aResult[1]) if aResult[0] else 0))

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sThumb = aEntry[0]
            siteUrl = aEntry[1]
            sTitle = aEntry[2].strip()

            sTitle = sTitle.replace("الجزء", "الموسم").replace("الموسم العاشر", "S10").replace("الموسم الحادي عشر", "S11").replace("الموسم الثاني عشر", "S12").replace("الموسم الثالث عشر", "S13").replace("الموسم الرابع عشر", "S14").replace("الموسم الخامس عشر", "S15").replace("الموسم السادس عشر", "S16").replace("الموسم السابع عشر", "S17").replace("الموسم الثامن عشر", "S18").replace("الموسم التاسع عشر", "S19").replace("الموسم العشرون", "S20").replace("الموسم الحادي و العشرون", "S21").replace("الموسم الثاني و العشرون", "S22").replace("الموسم الثالث و العشرون", "S23").replace("الموسم الرابع والعشرون", "S24").replace("الموسم الخامس و العشرون", "S25").replace("الموسم السادس والعشرون", "S26").replace("الموسم السابع والعشرون", "S27").replace("الموسم الثامن والعشرون", "S28").replace("الموسم التاسع والعشرون", "S29").replace("الموسم الثلاثون", "S30").replace("الموسم الحادي و الثلاثون", "S31").replace("الموسم الثاني والثلاثون", "S32").replace("الموسم الاول", "S1").replace("الموسم الثاني", "S2").replace("الموسم الثالث", "S3").replace("الموسم الثالث", "S3").replace("الموسم الرابع", "S4").replace("الموسم الخامس", "S5").replace("الموسم السادس", "S6").replace("الموسم السابع", "S7").replace("الموسم الثامن", "S8").replace("الموسم التاسع", "S9").replace("الموسم", "S").replace("موسم", "S").replace("S ", "S").replace("مدبلج", "").replace("مدبلجة", "").replace("مدبلجه", "").replace("الفلم", "").replace("الفيلم", "").replace("فلم", "").replace("فيلم", "").replace("مسلسل", "").replace("للعربية", "")
            sTitle = sTitle.strip()

            sDesc = ''

            oOutputParameterHandler.addParameter('siteUrl', siteUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)

            oGui.addTV(SITE_IDENTIFIER, 'showEpisodes', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

        sNextPage = __checkForNextPage(sHtmlContent)
        if sNextPage:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showSeries', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    if not sSearch:
        oGui.setEndOfDirectory()

def showEpisodes():
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    VSlog('[animeup] showEpisodes URL: %s' % sUrl)

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    if not sHtmlContent:
        VSlog('[animeup] showEpisodes: empty response')
        oGui.setEndOfDirectory()
        return

    VSlog('[animeup] showEpisodes: response length %d' % len(sHtmlContent))

    oParser = cParser()
    sPattern = r'<div class="ep_num">\s*<a href="([^"]+)">\s*([^<]+)</a>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    VSlog('[animeup] showEpisodes: found %d episodes' % (len(aResult[1]) if aResult[0] else 0))

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            siteUrl = aEntry[0]
            sTitle = aEntry[1].strip()

            sTitle = sTitle.replace("الحلقة ", " E").replace("حلقة ", " E").replace("الأخيرة", "")
            sTitle = sMovieTitle + sTitle

            oOutputParameterHandler.addParameter('siteUrl', siteUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oGui.addEpisode(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, '', oOutputParameterHandler)

        sNextPage = __checkForNextPage(sHtmlContent)
        if sNextPage:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showEpisodes', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def __checkForNextPage(sHtmlContent):
    sPattern = r'<a class="next page-numbers" href="([^"]+)">'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        return aResult[1][0]

    return False

def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    VSlog('[animeup] showHosters URL: %s' % sUrl)

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    if not sHtmlContent:
        VSlog('[animeup] showHosters: empty response')
        oGui.setEndOfDirectory()
        return

    VSlog('[animeup] showHosters: response length %d' % len(sHtmlContent))

    oParser = cParser()
    sPattern = r'<li[^>]+data-watch="([^"]+)"[^>]*>\s*<a[^>]*>\s*([^<\[]+)\s*(?:<span class="quality">\s*\[([^\]]+)\]</span>)?'
    aResult = oParser.parse(sHtmlContent, sPattern)

    VSlog('[animeup] showHosters: found %d servers' % (len(aResult[1]) if aResult[0] else 0))

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sHosterUrl = aEntry[0]
            sServerName = aEntry[1].strip()
            sQuality = aEntry[2].strip() if aEntry[2] else ''

            sDisplayTitle = sMovieTitle
            if sQuality:
                sDisplayTitle = ('%s [COLOR coral] [%s] %s[/COLOR]') % (sMovieTitle, sQuality, sServerName)
            elif sServerName:
                sDisplayTitle = ('%s [COLOR coral] %s[/COLOR]') % (sMovieTitle, sServerName)

            oHoster = cHosterGui().getHoster('resolver')
            oHoster.setRealHost(sServerName.upper())
            oHoster.setDisplayName(sDisplayTitle)
            oHoster.setFileName(sMovieTitle)
            cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)

    oGui.setEndOfDirectory()
