# -*- coding: utf-8 -*-

import re
import html as htmlmod

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import siteManager, addon

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/sites/logos/arblionz.png'

SITE_IDENTIFIER = 'arblionz'
SITE_NAME = 'Arblionz'
SITE_DESC = 'arabic vod'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER).rstrip('/')

URL_SEARCH = (URL_MAIN + '/wp-content/themes/ArabMovie/Inc/Ajax/SearchComplater.php?s=', 'showMovies')
URL_SEARCH_MOVIES = (URL_MAIN + '/wp-content/themes/ArabMovie/Inc/Ajax/SearchComplater.php?s=', 'showMovies')
URL_SEARCH_SERIES = (URL_MAIN + '/wp-content/themes/ArabMovie/Inc/Ajax/SearchComplater.php?s=', 'showSeries')
FUNCTION_SEARCH = 'showMovies'

AJAX_EPISODES = URL_MAIN + '/wp-content/themes/ArabMovie/Inc/Ajax/Single/Episodes.php'
AJAX_SEARCH = URL_MAIN + '/wp-content/themes/ArabMovie/Inc/Ajax/SearchComplater.php'


def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearchSeries', 'Search Series', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%d8%a3%d9%81%d9%84%d8%a7%d9%85-%d9%86%d8%aa%d9%81%d9%84%d9%8a%d9%83%d8%b3/')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام نتفليكس', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%d8%a7%d9%81%d9%84%d8%a7%d9%85-%d8%a7%d8%ac%d9%86%d8%a8%d9%8a/')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام أجنبية', icons + '/MoviesEnglish.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%d8%a7%d9%81%d9%84%d8%a7%d9%85-%d8%a7%d9%86%d9%8a%d9%85%d9%8a%d8%b4%d9%86/')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام أنيميشن', icons + '/Anime.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%d8%a7%d9%81%d9%84%d8%a7%d9%85-%d8%aa%d8%b1%d9%83%d9%8a%d8%a9/')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام تركية', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%d8%a7%d9%81%d9%84%d8%a7%d9%85-%d8%b9%d8%b1%d8%a8%d9%8a/')
    oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام عربية', icons + '/Arabic.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%d9%85%d8%b3%d9%84%d8%b3%d9%84%d8%a7%d8%aa-netfilx/')
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات Netfilx', icons + '/Series.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%d9%85%d8%b3%d9%84%d8%b3%d9%84%d8%a7%d8%aa-%d8%a7%d8%ac%d9%86%d8%a8%d9%8a/')
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات أجنبية', icons + '/Series.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%d9%85%d8%b3%d9%84%d8%b3%d9%84%d8%a7%d8%aa-%d8%aa%d8%b1%d9%83%d9%8a%d9%87/')
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات تركية', icons + '/Series.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%d9%85%d8%b3%d9%84%d8%b3%d9%84%d8%a7%d8%aa-%d8%b9%d8%b1%d8%a8%d9%8a/')
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات عربية', icons + '/Series.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%d9%85%d8%b3%d9%84%d8%b3%d9%84%d8%a7%d8%aa-%d9%83%d8%b1%d8%aa%d9%88%d9%86/')
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات كرتون', icons + '/Anime.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%d9%85%d8%b3%d9%84%d8%b3%d9%84%d8%a7%d8%aa-%d9%83%d9%88%d8%b1%d9%8a%d9%87/')
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'مسلسلات كورية', icons + '/Series.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_MAIN + '/category/%d8%a8%d8%b1%d8%a7%d9%85%d8%ac-%d8%aa%d9%84%d9%81%d8%b2%d9%8a%d9%88%d9%86%d9%8a%d8%a9/')
    oGui.addDir(SITE_IDENTIFIER, 'showSeries', 'برامج تلفزيونية', icons + '/Programs.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = AJAX_SEARCH + '?s=' + sSearchText
        showMovies(sUrl)
        oGui.setEndOfDirectory()
        return


def showSearchSeries():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = AJAX_SEARCH + '?s=' + sSearchText
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

    oParser = cParser()
    sPattern = r'<div class="BlockItem"><a href="([^"]+)"[^>]*>.*?data-image="([^"]+)"[^>]*alt="([^"]*)"[^>]*>.*?<h4>([^<]+)</h4>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sUrl2 = aEntry[0]
            sThumb = aEntry[1]
            sTitle = aEntry[3].strip()

            if 'فيلم' not in sTitle and 'عرض' not in sTitle:
                continue

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


def showSeries(sSearch=''):
    oGui = cGui()

    if sSearch:
        sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    oParser = cParser()
    sPattern = r'<div class="BlockItem"><a href="([^"]+)"[^>]*>.*?data-image="([^"]+)"[^>]*alt="([^"]*)"[^>]*>.*?<h4>([^<]+)</h4>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    itemList = []

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sUrl2 = aEntry[0]
            sThumb = aEntry[1]
            sTitle = aEntry[3].strip()

            if 'فيلم' in sTitle:
                continue

            sTitle = sTitle.replace('مشاهدة', '').replace('مسلسل', '').replace('انمي', '').replace('مترجمة', '').replace('مترجم', '').replace('مدبلج للعربية', 'مدبلج').replace('كاملة', '').replace('حلقات كاملة', '').replace('اونلاين', '').replace('مباشرة', '').replace('جودة عالية', '').replace('اون لاين', '').strip()

            sDisplayTitle = sTitle.split('الموسم')[0].split('الحلقة')[0].strip()

            if sDisplayTitle and sDisplayTitle not in itemList:
                itemList.append(sDisplayTitle)

                oOutputParameterHandler.addParameter('siteUrl', sUrl2)
                oOutputParameterHandler.addParameter('sMovieTitle', sDisplayTitle)
                oOutputParameterHandler.addParameter('sThumb', sThumb)

                oGui.addTV(SITE_IDENTIFIER, 'showSeasons', sDisplayTitle, '', sThumb, '', oOutputParameterHandler)

    if not sSearch:
        sNextPage = __checkForNextPage(sHtmlContent)
        if sNextPage:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showSeries', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)
        oGui.setEndOfDirectory()


def showSeasons():
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    m = re.search(r'<body[^>]*data-id="(\d+)"', sHtmlContent)
    sPostId = m.group(1) if m else ''

    oParser = cParser()
    sPattern = r'<a data-season="(\d+)"[^>]*>([^<]+)</a>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sSeasonId = aEntry[0]
            sTitle = aEntry[1].strip()

            sTitle = sTitle.replace('الموسم العاشر', 'S10').replace('الموسم الحادي عشر', 'S11').replace('الموسم الثاني عشر', 'S12').replace('الموسم الثالث عشر', 'S13').replace('الموسم الرابع عشر', 'S14').replace('الموسم الخامس عشر', 'S15').replace('الموسم السادس عشر', 'S16').replace('الموسم السابع عشر', 'S17').replace('الموسم الثامن عشر', 'S18').replace('الموسم التاسع عشر', 'S19').replace('الموسم العشرون', 'S20').replace('الموسم الحادي و العشرون', 'S21').replace('الموسم الثاني و العشرون', 'S22').replace('الموسم الثالث و العشرون', 'S23').replace('الموسم الرابع والعشرون', 'S24').replace('الموسم الخامس و العشرون', 'S25').replace('الموسم السادس والعشرون', 'S26').replace('الموسم السابع والعشرون', 'S27').replace('الموسم الثامن والعشرون', 'S28').replace('الموسم التاسع والعشرون', 'S29').replace('الموسم الثلاثون', 'S30').replace('الموسم الحادي و الثلاثون', 'S31').replace('الموسم الثاني والثلاثون', 'S32').replace('الموسم الاول', 'S1').replace('الموسم الأول', 'S1').replace('الموسم الثاني', 'S2').replace('الموسم الثالث', 'S3').replace('الموسم الرابع', 'S4').replace('الموسم الخامس', 'S5').replace('الموسم السادس', 'S6').replace('الموسم السابع', 'S7').replace('الموسم الثامن', 'S8').replace('الموسم التاسع', 'S9').replace('الموسم', 'S').replace('موسم', 'S').replace('S ', 'S')

            oOutputParameterHandler.addParameter('siteUrl', sUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle + ' - ' + sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('sSeasonId', sSeasonId)
            oOutputParameterHandler.addParameter('sPostId', sPostId)

            oGui.addSeason(SITE_IDENTIFIER, 'showEps', sTitle, '', sThumb, '', oOutputParameterHandler)

    else:
        sPattern = r'<div class="EpisodeItem[^"]*">\s*<a href="([^"]+)"[^>]*>.*?<span>الحلقة</span>\s*<em>(\d+)</em>'
        aResult = oParser.parse(sHtmlContent, sPattern)
        if aResult[0]:
            oOutputParameterHandler = cOutputParameterHandler()
            for aEntry in aResult[1]:
                sTitle = sMovieTitle + ' E' + aEntry[1]

                oOutputParameterHandler.addParameter('siteUrl', aEntry[0])
                oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
                oOutputParameterHandler.addParameter('sThumb', sThumb)

                oGui.addEpisode(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, '', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showEps():
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')
    sSeasonId = oInputParameterHandler.getValue('sSeasonId')
    sPostId = oInputParameterHandler.getValue('sPostId')

    if sSeasonId and sPostId:
        oRequestHandler = cRequestHandler(AJAX_EPISODES)
        oRequestHandler.setRequestType(1)
        oRequestHandler.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
        oRequestHandler.addHeaderEntry('Referer', sUrl)
        oRequestHandler.addHeaderEntry('Origin', URL_MAIN)
        oRequestHandler.addParameters({'season': sSeasonId, 'post_id': sPostId})
        sHtmlContent = oRequestHandler.request()
    else:
        oRequestHandler = cRequestHandler(sUrl)
        sHtmlContent = oRequestHandler.request()

    oParser = cParser()
    sPattern = r'<a href="([^"]+)"[^>]*>.*?<span>الحلقة</span>\s*<em>(\d+)</em>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()
        for aEntry in aResult[1]:
            sTitle = sMovieTitle + ' E' + aEntry[1]

            oOutputParameterHandler.addParameter('siteUrl', aEntry[0])
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

    if '?' in sUrl:
        sWatchUrl = sUrl + '&watch=1'
    else:
        sWatchUrl = sUrl + '?watch=1'

    oRequestHandler = cRequestHandler(sWatchUrl)
    sHtmlContent = oRequestHandler.request()

    oParser = cParser()
    servers = []

    sPattern = r'data-server-url="([^"]+)"'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        for aEntry in aResult[1]:
            sHosterUrl = htmlmod.unescape(aEntry)
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
            cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)

    oGui.setEndOfDirectory()


def __checkForNextPage(sHtmlContent):
    oParser = cParser()
    sPattern = r'<a class="next page-numbers" href="([^"]+)"'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if aResult[0]:
        return htmlmod.unescape(aResult[1][0])
    return False
