# -*- coding: utf-8 -*-
import json
import re
import urllib.parse

from resources.lib.gui.gui import cGui
from resources.lib.gui.hoster import cHosterGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.comaddon import VSlog, addon, dialog

URL_API = 'https://api3.shahid.net/proxy/v2.1'
COUNTRY = 'MA'
PAGE_SIZE = 30

DRM_TYPE = 'com.widevine.alpha'
DRM_LICENSE_KEY = 'https://shahid.la.drm.cloud/acquire-license/widevine?BrandGuid=2be49af0-6fbd-4511-8e11-3d6523185bb4'


def buildSite(sSiteIdentifier, sSiteName, sLang, sSiteDesc):
    icons = addon().getSetting('defaultIcons')
    LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/' + sSiteIdentifier + '.png'

    URL_MAIN = 'https://shahid.mbc.net/' + sLang
    URL_SEARCH = ('', 'showSearch')
    URL_SEARCH_DRAMAS = URL_SEARCH
    FUNCTION_SEARCH = 'showSearch'

    def _fetch(sUrl):
        oRequest = cRequestHandler(sUrl)
        oRequest.addHeaderEntry('user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36')
        oRequest.addHeaderEntry('language', 'AR')
        oRequest.addHeaderEntry('accept-language', 'ar')
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

    def _cleanMediaUrl(sUrl):
        # Le serveur renvoie parfois une url dupliquee (manifest.mpd&<host>/...)
        if re.search(r'\.(mpd|m3u8)&', sUrl):
            sUrl = sUrl.split('&')[0]
        return sUrl

    def _seasonLabel(iSeasonNumber):
        if sLang == 'ar':
            sWord = 'الموسم'
        elif sLang == 'fr':
            sWord = 'Saison'
        else:
            sWord = 'Season'
        return '%s %s' % (sWord, iSeasonNumber)

    def _episodeLabel(iNumber):
        if sLang == 'ar':
            return 'الحلقة %s' % iNumber
        if sLang == 'fr':
            return 'Épisode %s' % iNumber
        return 'Episode %s' % iNumber

    def load():
        oGui = cGui()

        try:
            dJson = _api('/editorial/page', {'pageAlias': 'free', 'profileFolder': 'NORTHAFRICA'})
            for oCarousel in dJson.get('carousels') or []:
                if oCarousel.get('type') != 'usecase' or not oCarousel.get('id'):
                    continue
                oAttrs = oCarousel.get('customAttributes') or {}
                if oAttrs.get('type') == 'live':
                    continue
                sLabel = oCarousel.get('displaytext') or oAttrs.get('title') or 'Shahid'
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', oCarousel.get('id'))
                oGui.addDir(sSiteIdentifier, 'showCarousel', sLabel, icons + '/Movies.png', oOutputParameterHandler)
        except Exception as e:
            VSlog('shahid: load failed (' + str(e) + ')')
            oGui.addText(sSiteIdentifier, '[COLOR red]Error loading Shahid[/COLOR]')

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
                oItem = oEntry.get('item') or {}
                sId = oItem.get('id')
                if not sId:
                    continue
                sTitle = oItem.get('title') or ''
                if isinstance(sTitle, dict):
                    sTitle = sTitle.get('ar') or ''
                sThumb = _img((oItem.get('image') or {}).get('thumbnailImage') or '')
                sDesc = oItem.get('description') or oItem.get('shortDescription') or ''

                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sId)
                oOutputParameterHandler.addParameter('sTitle', sTitle)
                oOutputParameterHandler.addParameter('sThumb', sThumb)
                oOutputParameterHandler.addParameter('sDrmType', DRM_TYPE)
                oOutputParameterHandler.addParameter('sDrmLicenseKey', DRM_LICENSE_KEY)

                if oItem.get('productType') == 'SHOW':
                    oGui.addDrama(sSiteIdentifier, 'showContent', sTitle,
                                  sThumb if sThumb else icons + '/TVShows.png', sThumb, sDesc,
                                  oOutputParameterHandler)
                elif oItem.get('productType') == 'MOVIE':
                    oGui.addMovie(sSiteIdentifier, 'showPlay', sTitle,
                                  sThumb if sThumb else icons + '/Movies.png', sThumb, sDesc,
                                  oOutputParameterHandler)

            if dJson.get('hasMore'):
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sCarouselId)
                oOutputParameterHandler.addParameter('sPage', str(iPage + 1))
                oGui.addDir(sSiteIdentifier, 'showCarousel', '[COLOR teal]Next >>>[/COLOR]',
                            icons + '/Next.png', oOutputParameterHandler)
        except Exception as e:
            VSlog('shahid: showCarousel failed (' + str(e) + ')')
            oGui.addText(sSiteIdentifier, '[COLOR red]Error loading carousel[/COLOR]')

        oGui.setEndOfDirectory()

    def showContent():
        oGui = cGui()
        oInputParameterHandler = cInputParameterHandler()
        sShowId = oInputParameterHandler.getValue('siteUrl')
        sTitle = oInputParameterHandler.getValue('sTitle') or 'Shahid'
        sThumb = oInputParameterHandler.getValue('sThumb')

        try:
            dJson = _api('/product/id', {'id': int(sShowId), 'productType': 'SHOW', 'productSubType': 'SERIES'})
            oModel = dJson.get('productModel') or {}
            if not sThumb:
                sThumb = _img((oModel.get('image') or {}).get('posterImage') or '')
            for oSeason in oModel.get('seasons') or []:
                sSeasonId = oSeason.get('id')
                if not sSeasonId:
                    continue
                sLabel = _seasonLabel(oSeason.get('seasonNumber') or 0)
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sSeasonId)
                oOutputParameterHandler.addParameter('sTitle', sTitle)
                oOutputParameterHandler.addParameter('sThumb', sThumb)
                oGui.addDir(sSiteIdentifier, 'showEpisodes', sLabel,
                            sThumb if sThumb else icons + '/TVShows.png', oOutputParameterHandler)

            if not oModel.get('seasons'):
                oGui.addText(sSiteIdentifier, '[COLOR gray]No seasons available[/COLOR]')
        except Exception as e:
            VSlog('shahid: showContent failed (' + str(e) + ')')
            oGui.addText(sSiteIdentifier, '[COLOR red]Error loading seasons[/COLOR]')

        oGui.setEndOfDirectory()

    def showEpisodes():
        oGui = cGui()
        oInputParameterHandler = cInputParameterHandler()
        sSeasonId = oInputParameterHandler.getValue('siteUrl')
        sTitle = oInputParameterHandler.getValue('sTitle') or 'Shahid'
        sThumb = oInputParameterHandler.getValue('sThumb')
        sPage = oInputParameterHandler.getValue('sPage')
        iPage = int(sPage) if sPage else 0

        try:
            dJson = _api('/product/playlistsBySeason',
                         {'seasonIds': [int(sSeasonId)], 'pageNumber': iPage, 'pageSize': PAGE_SIZE, 'productSubType': 'EPISODE'})
            for oProduct in (dJson.get('productList') or {}).get('products') or []:
                sEpId = oProduct.get('id')
                if not sEpId:
                    continue
                sLabel = _episodeLabel(oProduct.get('number') or 0)
                sEpThumb = _img((oProduct.get('thumbnailImage') or '') or sThumb)
                sDesc = oProduct.get('description') or oProduct.get('shortDescription') or ''
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sEpId)
                oOutputParameterHandler.addParameter('sTitle', sLabel)
                oOutputParameterHandler.addParameter('sThumb', sEpThumb)
                oOutputParameterHandler.addParameter('sDrmType', DRM_TYPE)
                oOutputParameterHandler.addParameter('sDrmLicenseKey', DRM_LICENSE_KEY)
                oGui.addEpisode(sSiteIdentifier, 'showPlay', sLabel,
                                sEpThumb if sEpThumb else icons + '/TVShows.png', sEpThumb, sDesc,
                                oOutputParameterHandler)

            if (dJson.get('productList') or {}).get('hasMore'):
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sSeasonId)
                oOutputParameterHandler.addParameter('sTitle', sTitle)
                oOutputParameterHandler.addParameter('sThumb', sThumb)
                oOutputParameterHandler.addParameter('sPage', str(iPage + 1))
                oGui.addDir(sSiteIdentifier, 'showEpisodes', '[COLOR teal]Next >>>[/COLOR]',
                            icons + '/Next.png', oOutputParameterHandler)
        except Exception as e:
            VSlog('shahid: showEpisodes failed (' + str(e) + ')')
            oGui.addText(sSiteIdentifier, '[COLOR red]Error loading episodes[/COLOR]')

        oGui.setEndOfDirectory()

    def showPlay():
        oGui = cGui()
        oInputParameterHandler = cInputParameterHandler()
        sProductId = oInputParameterHandler.getValue('siteUrl')
        sTitle = oInputParameterHandler.getValue('sTitle') or sSiteName
        sThumb = oInputParameterHandler.getValue('sThumb')

        try:
            sContent = _fetch(URL_API + '/playout/new/url/' + str(sProductId) + '?country=' + COUNTRY)
            dJson = json.loads(sContent)
            oPlayout = dJson.get('playout') or dJson

            aMediaUrls = oPlayout.get('mediaUrls') or []
            if not aMediaUrls:
                dialog().VSinfo('[COLOR red]No stream available[/COLOR]', sSiteName)
                oGui.setEndOfDirectory()
                return

            sMediaUrl = _cleanMediaUrl(aMediaUrls[0].get('url') or '')
            if not sMediaUrl:
                dialog().VSinfo('[COLOR red]No stream available[/COLOR]', sSiteName)
                oGui.setEndOfDirectory()
                return

            oHoster = cHosterGui().getHoster('lien_direct')
            oHoster.setDisplayName(sTitle)
            oHoster.setFileName(sTitle)
            sLicense = DRM_LICENSE_KEY
            sRestrictionsToken = oPlayout.get('restrictionsToken') or ''
            if sRestrictionsToken:
                sLicense = '%s|x-dt-auth-token=%s|R{SSM}|R' % (DRM_LICENSE_KEY, sRestrictionsToken)
            cHosterGui().showHoster(oGui, oHoster, sMediaUrl, sThumb, sDrmLicenseKey=sLicense)
        except Exception as e:
            VSlog('shahid: showPlay failed (' + str(e) + ')')
            dialog().VSinfo('[COLOR red]Error resolving stream[/COLOR]', sSiteName)

        oGui.setEndOfDirectory()

    def showSearch(sSearchText=''):
        oGui = cGui()
        oGui.addText(sSiteIdentifier, '[COLOR gray]Search not available for this source[/COLOR]')
        oGui.setEndOfDirectory()

    return {
        'SITE_IDENTIFIER': sSiteIdentifier,
        'SITE_NAME': sSiteName,
        'SITE_DESC': sSiteDesc,
        'LOGO': LOGO,
        'URL_MAIN': URL_MAIN,
        'URL_SEARCH': URL_SEARCH,
        'URL_SEARCH_DRAMAS': URL_SEARCH_DRAMAS,
        'FUNCTION_SEARCH': FUNCTION_SEARCH,
        'load': load,
        'showCarousel': showCarousel,
        'showContent': showContent,
        'showEpisodes': showEpisodes,
        'showPlay': showPlay,
        'showSearch': showSearch,
    }
