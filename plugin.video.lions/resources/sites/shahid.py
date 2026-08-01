# -*- coding: utf-8 -*-
import json
import urllib.parse

from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.comaddon import VSlog, addon

URL_API = 'https://api3.shahid.net/proxy/v2.1'
COUNTRY = 'MA'
PAGE_SIZE = 30
TOP_RANKING_PAGE_SIZE = 25


def buildSite(sSiteIdentifier, sSiteName, sLang, sSiteDesc):
    icons = addon().getSetting('defaultIcons')
    LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/' + sSiteIdentifier + '.png'

    URL_MAIN = 'https://shahid.mbc.net/' + sLang

    sLangUpper = sLang.upper()
    sProfileId = 'f87e79c0-8cba-11f1-a579-c77f29a076a2'
    sProfileKey = '{"ageRestriction":false,"isAdult":true}'

    def _label(sAr, sFr, sEn):
        if sLang == 'ar':
            return sAr
        if sLang == 'fr':
            return sFr
        return sEn

    def _fetch(sUrl):
        oRequest = cRequestHandler(sUrl)
        oRequest.addHeaderEntry('user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36')
        oRequest.addHeaderEntry('language', sLangUpper)
        oRequest.addHeaderEntry('accept-language', sLang)
        oRequest.addHeaderEntry('uuid', 'web')
        oRequest.addHeaderEntry('profile', '{"ageRestriction":false,"id":"' + sProfileId + '","master":true}')
        oRequest.addHeaderEntry('profile-key', sProfileKey)
        return oRequest.request()

    def _api(sPath, dParams):
        sUrl = URL_API + sPath + '?request=' + urllib.parse.quote(json.dumps(dParams, separators=(',', ':')), safe='') + '&country=' + COUNTRY
        sContent = _fetch(sUrl)
        try:
            return json.loads(sContent)
        except Exception as e:
            VSlog('shahid: json decode failed (' + str(e) + ')')
            return {}

    def _img(sUrl):
        if not sUrl:
            return ''
        return sUrl.replace('{height}', '250').replace('{width}', '160') \
                  .replace('{croppingPoint}', 'original').replace('{version}', '1')

    def _fanart(sUrl):
        if not sUrl:
            return ''
        return sUrl.replace('{height}', '720').replace('{width}', '1280') \
                  .replace('{croppingPoint}', 'original').replace('{version}', '1')

    def _year(oItem):
        for sKey in ('productionDate', 'releaseDate'):
            sVal = oItem.get(sKey) or ''
            if len(sVal) >= 4 and sVal[:4].isdigit():
                iYear = int(sVal[:4])
                if 1900 < iYear <= 2100:
                    return sVal[:4]
        return ''

    def _itemMeta(oItem):
        oImage = oItem.get('image') or {}
        sTitle = oItem.get('title') or ''
        if isinstance(sTitle, dict):
            sTitle = sTitle.get(sLang) or sTitle.get('ar') or sTitle.get('en') or ''
        sThumb = _img(oImage.get('posterImage') or oItem.get('thumbnailImage') or oImage.get('thumbnailImage') or '')
        sFanart = _fanart(oImage.get('heroSliderImage') or '')
        sDesc = oItem.get('description') or oItem.get('shortDescription') or ''
        sYear = _year(oItem)
        sGenre = '/'.join([g.get('title') or '' for g in (oItem.get('genres') or []) if g.get('title')])
        aCast = [c for c in (p.get('fullName') or p.get('firstName') or '' for p in (oItem.get('persons') or [])) if c][:8]
        if aCast:
            sCast = _label('الممثلون', 'Distribution', 'Cast') + ': ' + ', '.join(aCast)
            sDesc = (sDesc + '\n' + sCast) if sDesc else sCast
        return sTitle, sThumb, sFanart, sDesc, sYear, sGenre

    def _seasonLabel(iSeasonNumber, iEpisodeCount=0):
        sWord = _label('الموسم', 'Saison', 'Season')
        sLabel = '%s %s' % (sWord, iSeasonNumber)
        if iEpisodeCount:
            sLabel += ' (%s)' % iEpisodeCount
        return sLabel

    def _episodeLabel(iNumber):
        return _label('الحلقة %s' % iNumber, 'Épisode %s' % iNumber, 'Episode %s' % iNumber)

    def _toInt(sVal):
        try:
            return int(sVal)
        except (TypeError, ValueError):
            return sVal

    def _nextLabel():
        return '[COLOR teal]Next >>>[/COLOR]'

    def _searchSourcesLabel():
        return _label('البحث عن مصادر', 'Rechercher des sources', 'Search sources')

    def _addCatalogItem(oGui, oItem):
        sId = oItem.get('id')
        if not sId:
            return
        sTitle, sThumb, sFanart, sDesc, sYear, sGenre = _itemMeta(oItem)
        if not sTitle:
            return

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sId)
        oOutputParameterHandler.addParameter('sTitle', sTitle)
        oOutputParameterHandler.addParameter('sThumb', sThumb)
        oOutputParameterHandler.addParameter('sFanart', sFanart)

        oGuiElement = cGuiElement()
        oGuiElement.setTitle(sTitle)
        oGuiElement.setFileName(sTitle)
        oGuiElement.setDescription(sDesc)
        oGuiElement.setYear(sYear)
        oGuiElement.setGenre(sGenre)
        oGuiElement.setPoster(sThumb)
        oGuiElement.setThumbnail(sThumb)
        oGuiElement.setFanart(sFanart)
        oGuiElement.setMeta(1)

        if oItem.get('productType') == 'SHOW':
            oGuiElement.setSiteName(sSiteIdentifier)
            oGuiElement.setFunction('showSeasons')
            oGuiElement.setIcon(icons + '/TVShows.png')
            oGuiElement.setCat(2)
            oGuiElement.setMeta(2)
            cGui.CONTENT = 'tvshows'
        else:
            oGuiElement.setSiteName('globalSearch')
            oGuiElement.setFunction('showSearch')
            oGuiElement.setIcon(icons + '/Movies.png')
            oGuiElement.setCat(1)
            oOutputParameterHandler.addParameter('searchtext', sTitle)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            cGui.CONTENT = 'movies'

        oGui.addFolder(oGuiElement, oOutputParameterHandler)

    def _addEpisodeItem(oGui, oProduct, sShowTitle, sThumb, sFanart):
        sId = oProduct.get('id')
        if not sId:
            return
        sLabel = _episodeLabel(oProduct.get('number') or 0)
        sEpThumb = _img(oProduct.get('thumbnailImage') or '') or sThumb
        sDesc = oProduct.get('description') or oProduct.get('shortDescription') or ''

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sShowTitle)
        oOutputParameterHandler.addParameter('searchtext', sShowTitle)
        oOutputParameterHandler.addParameter('sMovieTitle', sShowTitle)
        oOutputParameterHandler.addParameter('sThumb', sEpThumb)

        oGuiElement = cGuiElement()
        oGuiElement.setSiteName('globalSearch')
        oGuiElement.setFunction('showSearch')
        oGuiElement.setTitle(sLabel)
        oGuiElement.setFileName(sShowTitle)
        oGuiElement.setIcon(icons + '/TVShows.png')
        oGuiElement.setMeta(2)
        oGuiElement.setCat(2)
        oGuiElement.setThumbnail(sEpThumb)
        oGuiElement.setPoster(sEpThumb)
        oGuiElement.setFanart(sFanart)
        oGuiElement.setDescription(sDesc)
        cGui.CONTENT = 'episodes'
        oGui.addFolder(oGuiElement, oOutputParameterHandler)

    def _heroCarouselId(sAlias):
        try:
            dJson = _api('/editorial/page', {'pageAlias': sAlias, 'profileFolder': 'NORTHAFRICA'})
            for oCarousel in dJson.get('carousels') or []:
                if oCarousel.get('type') != 'usecase' or not oCarousel.get('id'):
                    continue
                if (oCarousel.get('customAttributes') or {}).get('type') == 'live':
                    continue
                return oCarousel.get('id')
        except Exception as e:
            VSlog('shahid: hero lookup failed (' + str(e) + ')')
        return ''

    def load():
        oGui = cGui()

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', 'http://')
        oGui.addDir(sSiteIdentifier, 'showSearch', _label('بحث', 'Recherche', 'Search'), icons + '/Search.png', oOutputParameterHandler)

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('sType', 'movie')
        oGui.addDir(sSiteIdentifier, 'showTop', _label('أفضل 10 أفلام', 'Top 10 Films', 'Top 10 Movies'), icons + '/Top.png', oOutputParameterHandler)

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('sType', 'series')
        oGui.addDir(sSiteIdentifier, 'showTop', _label('أفضل 10 مسلسلات', 'Top 10 Séries', 'Top 10 Series'), icons + '/Top.png', oOutputParameterHandler)

        for sAlias, sLabel in (
            ('free', _label('تشكيلة مجانية', 'Sélection gratuite', 'Free Picks')),
            ('series', _label('تشكيلة مسلسلات', 'Sélection de séries', 'Series Picks')),
            ('movies', _label('تشكيلة أفلام', 'Sélection de films', 'Movies Picks')),
        ):
            sHeroId = _heroCarouselId(sAlias)
            if sHeroId:
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sHeroId)
                oGui.addDir(sSiteIdentifier, 'showCarousel', sLabel, icons + '/Movies.png', oOutputParameterHandler)

        oGui.setEndOfDirectory()

    def showSearch(sSearchText=''):
        oGui = cGui()
        if not sSearchText:
            sSearchText = oGui.showKeyBoard()
            if not sSearchText:
                oGui.setEndOfDirectory()
                return

        for sTab, sLabel in (('TV_SHOWS', _label('مسلسلات', 'Séries', 'TV Shows')),
                             ('MOVIES', _label('أفلام', 'Films', 'Movies'))):
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('sSearchText', sSearchText)
            oOutputParameterHandler.addParameter('sTab', sTab)
            oGui.addDir(sSiteIdentifier, 'showSearchTab', sLabel, icons + '/Search.png', oOutputParameterHandler)

        oGui.setEndOfDirectory()

    def showSearchTab():
        oGui = cGui()
        oInputParameterHandler = cInputParameterHandler()
        sSearchText = oInputParameterHandler.getValue('sSearchText')
        sTab = oInputParameterHandler.getValue('sTab')
        sPage = oInputParameterHandler.getValue('sPage')
        iPage = int(sPage) if sPage else 0

        try:
            dJson = _api('/search/' + sTab, {'name': sSearchText, 'pageNumber': iPage, 'pageSize': PAGE_SIZE})
            for oItem in dJson.get('productList') or []:
                _addCatalogItem(oGui, oItem)
            if not dJson.get('productList'):
                oGui.addText(sSiteIdentifier, '[COLOR gray]No results[/COLOR]')
            if dJson.get('hasMore'):
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('sSearchText', sSearchText)
                oOutputParameterHandler.addParameter('sTab', sTab)
                oOutputParameterHandler.addParameter('sPage', str(iPage + 1))
                oGui.addDir(sSiteIdentifier, 'showSearchTab', _nextLabel(), icons + '/Next.png', oOutputParameterHandler)
        except Exception as e:
            VSlog('shahid: showSearchTab failed (' + str(e) + ')')
            oGui.addText(sSiteIdentifier, '[COLOR red]Error loading search results[/COLOR]')

        oGui.setEndOfDirectory()

    def showTop():
        oGui = cGui()
        oInputParameterHandler = cInputParameterHandler()
        sType = oInputParameterHandler.getValue('sType') or 'series'

        try:
            dJson = _api('/product/top-ranking-by-type', {'pageNumber': 0, 'pageSize': TOP_RANKING_PAGE_SIZE, 'profileType': 'MIXED'})
            oTop = (dJson.get('top') or {}).get(sType) or {}
            for oItem in oTop.get('products') or []:
                _addCatalogItem(oGui, oItem)
            if not oTop.get('products'):
                oGui.addText(sSiteIdentifier, '[COLOR gray]No results[/COLOR]')
        except Exception as e:
            VSlog('shahid: showTop failed (' + str(e) + ')')
            oGui.addText(sSiteIdentifier, '[COLOR red]Error loading ranking[/COLOR]')

        oGui.setEndOfDirectory()

    def showCarousel():
        oGui = cGui()
        oInputParameterHandler = cInputParameterHandler()
        sCarouselId = oInputParameterHandler.getValue('siteUrl')
        sPage = oInputParameterHandler.getValue('sPage')
        iPage = int(sPage) if sPage else 0

        try:
            dJson = _api('/editorial/carousel', {'pageNumber': iPage, 'pageSize': PAGE_SIZE, 'id': sCarouselId})
            for oEntry in dJson.get('editorialItems') or []:
                _addCatalogItem(oGui, oEntry.get('item') or {})
            if not dJson.get('editorialItems'):
                oGui.addText(sSiteIdentifier, '[COLOR gray]No results[/COLOR]')
            if dJson.get('hasMore'):
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sCarouselId)
                oOutputParameterHandler.addParameter('sPage', str(iPage + 1))
                oGui.addDir(sSiteIdentifier, 'showCarousel', _nextLabel(), icons + '/Next.png', oOutputParameterHandler)
        except Exception as e:
            VSlog('shahid: showCarousel failed (' + str(e) + ')')
            oGui.addText(sSiteIdentifier, '[COLOR red]Error loading carousel[/COLOR]')

        oGui.setEndOfDirectory()

    def showSeasons():
        oGui = cGui()
        oInputParameterHandler = cInputParameterHandler()
        sShowId = oInputParameterHandler.getValue('siteUrl')
        sTitle = oInputParameterHandler.getValue('sTitle') or sSiteName
        sThumb = oInputParameterHandler.getValue('sThumb')
        sFanart = oInputParameterHandler.getValue('sFanart')

        try:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sShowId)
            oOutputParameterHandler.addParameter('searchtext', sTitle)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oGuiElement = cGuiElement()
            oGuiElement.setSiteName('globalSearch')
            oGuiElement.setFunction('showSearch')
            oGuiElement.setTitle(_searchSourcesLabel())
            oGuiElement.setFileName(sTitle)
            oGuiElement.setIcon(icons + '/Search.png')
            oGuiElement.setMeta(2)
            oGuiElement.setCat(2)
            oGuiElement.setThumbnail(sThumb)
            oGuiElement.setPoster(sThumb)
            oGuiElement.setFanart(sFanart)
            oGui.addFolder(oGuiElement, oOutputParameterHandler)

            dJson = _api('/product/id', {'id': _toInt(sShowId), 'productType': 'SHOW', 'productSubType': 'SERIES'})
            oModel = dJson.get('productModel') or {}
            if not sThumb:
                sThumb = _img(((oModel.get('image') or {}).get('posterImage')) or '')
            if not sFanart:
                sFanart = _fanart(((oModel.get('image') or {}).get('heroSliderImage')) or '')
            for oSeason in oModel.get('seasons') or []:
                sSeasonId = oSeason.get('id')
                if not sSeasonId:
                    continue
                sLabel = _seasonLabel(oSeason.get('seasonNumber') or 0, oSeason.get('numberOfAVODEpisodes') or 0)
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sSeasonId)
                oOutputParameterHandler.addParameter('sTitle', sTitle)
                oOutputParameterHandler.addParameter('sThumb', sThumb)
                oOutputParameterHandler.addParameter('sFanart', sFanart)
                oGui.addDir(sSiteIdentifier, 'showEpisodes', sLabel,
                            sThumb if sThumb else icons + '/TVShows.png', oOutputParameterHandler)

            if not oModel.get('seasons'):
                oGui.addText(sSiteIdentifier, '[COLOR gray]No seasons available[/COLOR]')
        except Exception as e:
            VSlog('shahid: showSeasons failed (' + str(e) + ')')
            oGui.addText(sSiteIdentifier, '[COLOR red]Error loading seasons[/COLOR]')

        oGui.setEndOfDirectory()

    def showEpisodes():
        oGui = cGui()
        oInputParameterHandler = cInputParameterHandler()
        sSeasonId = oInputParameterHandler.getValue('siteUrl')
        sTitle = oInputParameterHandler.getValue('sTitle') or sSiteName
        sThumb = oInputParameterHandler.getValue('sThumb')
        sFanart = oInputParameterHandler.getValue('sFanart')
        sPage = oInputParameterHandler.getValue('sPage')
        iPage = int(sPage) if sPage else 0

        try:
            dJson = _api('/product/playlistsBySeason',
                         {'seasonIds': [_toInt(sSeasonId)], 'pageNumber': iPage, 'pageSize': PAGE_SIZE, 'productSubType': 'EPISODE'})
            oProductList = dJson.get('productList') or {}
            for oProduct in oProductList.get('products') or []:
                _addEpisodeItem(oGui, oProduct, sTitle, sThumb, sFanart)
            if not oProductList.get('products'):
                oGui.addText(sSiteIdentifier, '[COLOR gray]No episodes available[/COLOR]')
            if oProductList.get('hasMore'):
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sSeasonId)
                oOutputParameterHandler.addParameter('sTitle', sTitle)
                oOutputParameterHandler.addParameter('sThumb', sThumb)
                oOutputParameterHandler.addParameter('sFanart', sFanart)
                oOutputParameterHandler.addParameter('sPage', str(iPage + 1))
                oGui.addDir(sSiteIdentifier, 'showEpisodes', _nextLabel(), icons + '/Next.png', oOutputParameterHandler)
        except Exception as e:
            VSlog('shahid: showEpisodes failed (' + str(e) + ')')
            oGui.addText(sSiteIdentifier, '[COLOR red]Error loading episodes[/COLOR]')

        oGui.setEndOfDirectory()

    return {
        'SITE_IDENTIFIER': sSiteIdentifier,
        'SITE_NAME': sSiteName,
        'SITE_DESC': sSiteDesc,
        'LOGO': LOGO,
        'URL_MAIN': URL_MAIN,
        'load': load,
        'showSearch': showSearch,
        'showSearchTab': showSearchTab,
        'showTop': showTop,
        'showCarousel': showCarousel,
        'showSeasons': showSeasons,
        'showEpisodes': showEpisodes,
    }
