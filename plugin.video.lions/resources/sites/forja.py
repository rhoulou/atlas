# -*- coding: utf-8 -*-
import json
import urllib.parse

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.comaddon import VSlog, addon

URL_MAIN = 'https://forja.ma'

CATEGORIES = (
    ('Films', 'films', '/Movies.png'),
    ('Séries', 'series', '/TVShows.png'),
    ('Théâtre', 'theatre', '/Movies.png'),
    ('Divertissement', 'divertissement', '/Misc.png'),
    ('Documentaires', 'fnqxzgjwehxiksgbfujypbplresdjsiegtngcqwm', '/Documentary.png'),
    ('Enfants', 'uvrqdsllaeoaxfporlrbsqehcyffsoufneihoyow', '/Kids.png'),
)

PAGE_SIZE = 40


def buildSite(sSiteIdentifier, sSiteName, sLang, sSiteDesc):
    icons = addon().getSetting('defaultIcons')
    LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/' + sSiteIdentifier + '.png'

    URL_SEARCH = (URL_MAIN + '/pages/searchForja/?filter=', 'showSearch')
    URL_SEARCH_DRAMAS = URL_SEARCH
    FUNCTION_SEARCH = 'showSearch'

    def _fetch(sUrl):
        oRequest = cRequestHandler(sUrl)
        oRequest.addHeaderEntry('user-agent', 'Mozilla/5.0')
        return oRequest.request()

    def _proxyUrl(sContentId):
        return URL_MAIN + '/pages/proxy/content/' + str(sContentId) + '/stream_url?mode=link&lang=' + sLang

    def _showItems(oGui, aItems):
        for oItem in aItems:
            sTitle = oItem.get('name') or oItem.get('name_long') or ''
            sThumb = oItem.get('tile_image') or oItem.get('poster_image') or ''
            sDesc = oItem.get('description_short') or oItem.get('description') or ''

            oOutputParameterHandler = cOutputParameterHandler()
            if oItem.get('type') == 'playlist':
                if not oItem.get('slug'):
                    continue
                oOutputParameterHandler.addParameter('siteUrl', oItem.get('slug'))
                oOutputParameterHandler.addParameter('sTitle', sTitle)
                oOutputParameterHandler.addParameter('sThumb', sThumb)
                oGui.addDrama(sSiteIdentifier, 'showContent', sTitle,
                              sThumb if sThumb else icons + '/TVShows.png', sThumb, sDesc,
                              oOutputParameterHandler)
            else:
                if not oItem.get('id'):
                    continue
                oOutputParameterHandler.addParameter('siteUrl', _proxyUrl(oItem.get('id')))
                oOutputParameterHandler.addParameter('sLang', sLang)
                oOutputParameterHandler.addParameter('sTitle', sTitle)
                oOutputParameterHandler.addParameter('sThumb', sThumb)
                oGui.addMovie(sSiteIdentifier, 'showHosters', sTitle,
                              sThumb if sThumb else icons + '/Movies.png', sThumb, sDesc,
                              oOutputParameterHandler)

    def load():
        oGui = cGui()
        for sLabel, sCatSlug, sIcon in CATEGORIES:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sCatSlug)
            oGui.addDir(sSiteIdentifier, 'showCategory', sLabel, icons + sIcon, oOutputParameterHandler)

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', 'search')
        oGui.addDir(sSiteIdentifier, 'showSearch', 'Search', icons + '/Search.png', oOutputParameterHandler)

        oGui.setEndOfDirectory()

    def showCategory():
        oGui = cGui()
        oInputParameterHandler = cInputParameterHandler()
        sCatSlug = oInputParameterHandler.getValue('siteUrl')

        try:
            sUrl = URL_MAIN + '/pages/category/' + sCatSlug + '/more?page=1&filter=no-age-restriction&lang=' + sLang
            dJson = json.loads(_fetch(sUrl))
            _showItems(oGui, dJson.get('data') or [])
        except Exception as e:
            VSlog('forja: showCategory failed (' + str(e) + ')')
            oGui.addText(sSiteIdentifier, '[COLOR red]Error loading category[/COLOR]')

        oGui.setEndOfDirectory()

    def showContent():
        oGui = cGui()
        oInputParameterHandler = cInputParameterHandler()
        sSlug = oInputParameterHandler.getValue('siteUrl')

        try:
            sUrl = URL_MAIN + '/pages/content/' + sSlug + '?lang=' + sLang
            dJson = json.loads(_fetch(sUrl))

            if dJson.get('type') == 'playlist':
                oPoster = dJson.get('tile_image') or dJson.get('poster_image') or ''
                for oSeason in dJson.get('contents') or []:
                    for iEp, oEpisode in enumerate(oSeason.get('contents') or [], start=1):
                        sEpName = oEpisode.get('name') or ('Episode %d' % iEp)
                        sEpThumb = oEpisode.get('tile_image') or oEpisode.get('poster_image') or oPoster
                        sEpDesc = oEpisode.get('description_short') or oEpisode.get('description') or ''
                        if not oEpisode.get('id'):
                            continue
                        oOutputParameterHandler = cOutputParameterHandler()
                        oOutputParameterHandler.addParameter('siteUrl', _proxyUrl(oEpisode.get('id')))
                        oOutputParameterHandler.addParameter('sLang', sLang)
                        oOutputParameterHandler.addParameter('sTitle', sEpName)
                        oOutputParameterHandler.addParameter('sThumb', sEpThumb)
                        oGui.addEpisode(sSiteIdentifier, 'showHosters', sEpName,
                                        sEpThumb if sEpThumb else icons + '/Movies.png', sEpThumb, sEpDesc,
                                        oOutputParameterHandler)
            else:
                if not dJson.get('id'):
                    oGui.addText(sSiteIdentifier, '[COLOR red]No content available[/COLOR]')
                else:
                    sTitle = dJson.get('name') or ''
                    sThumb = dJson.get('tile_image') or dJson.get('poster_image') or ''
                    sDesc = dJson.get('description_short') or dJson.get('description') or ''
                    oOutputParameterHandler = cOutputParameterHandler()
                    oOutputParameterHandler.addParameter('siteUrl', _proxyUrl(dJson.get('id')))
                    oOutputParameterHandler.addParameter('sLang', sLang)
                    oOutputParameterHandler.addParameter('sTitle', sTitle)
                    oOutputParameterHandler.addParameter('sThumb', sThumb)
                    oGui.addMovie(sSiteIdentifier, 'showHosters', sTitle,
                                  sThumb if sThumb else icons + '/Movies.png', sThumb, sDesc,
                                  oOutputParameterHandler)
        except Exception as e:
            VSlog('forja: showContent failed (' + str(e) + ')')
            oGui.addText(sSiteIdentifier, '[COLOR red]Error loading content[/COLOR]')

        oGui.setEndOfDirectory()

    def showSearch(sSearchText=''):
        oGui = cGui()
        oInputParameterHandler = cInputParameterHandler()
        sPage = oInputParameterHandler.getValue('sPage')

        sQuery = ''
        if sSearchText.startswith('http'):
            sQuery = urllib.parse.unquote(sSearchText.split('filter=', 1)[-1])
        else:
            sQuery = oInputParameterHandler.getValue('siteUrl')

        if not sQuery:
            sQuery = oGui.showKeyBoard()
            if not sQuery:
                oGui.setEndOfDirectory()
                return

        iPage = int(sPage) if sPage else 1
        try:
            sUrl = URL_SEARCH[0] + urllib.parse.quote_plus(sQuery) + \
                ('&year=&categories=&direction=asc&page=%d&page_size=%d&origin=search&types=&lang=' % (iPage, PAGE_SIZE)) + sLang
            dJson = json.loads(_fetch(sUrl))
            oContents = dJson.get('contents') or {}
            _showItems(oGui, oContents.get('data') or [])

            if iPage < (oContents.get('lastPage') or 1):
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sQuery)
                oOutputParameterHandler.addParameter('sPage', str(iPage + 1))
                oGui.addDir(sSiteIdentifier, 'showSearch', '[COLOR teal]Next >>>[/COLOR]',
                            icons + '/Next.png', oOutputParameterHandler)
        except Exception as e:
            VSlog('forja: showSearch failed (' + str(e) + ')')
            oGui.addText(sSiteIdentifier, '[COLOR red]Error searching[/COLOR]')

        oGui.setEndOfDirectory()

    def showHosters():
        oGui = cGui()
        oInputParameterHandler = cInputParameterHandler()
        sProxyUrl = oInputParameterHandler.getValue('siteUrl')
        sTitle = oInputParameterHandler.getValue('sTitle') or 'Forja'
        sThumb = oInputParameterHandler.getValue('sThumb')

        oHoster = cHosterGui().getHoster('forja_ma')
        oHoster.setDisplayName(sTitle)
        oHoster.setFileName(sTitle)
        cHosterGui().showHoster(oGui, oHoster, sProxyUrl, sThumb)

        oGui.setEndOfDirectory()

    return {
        'SITE_IDENTIFIER': sSiteIdentifier,
        'SITE_NAME': sSiteName,
        'SITE_DESC': sSiteDesc,
        'LOGO': LOGO,
        'URL_SEARCH': URL_SEARCH,
        'URL_SEARCH_DRAMAS': URL_SEARCH_DRAMAS,
        'FUNCTION_SEARCH': FUNCTION_SEARCH,
        'load': load,
        'showCategory': showCategory,
        'showContent': showContent,
        'showSearch': showSearch,
        'showHosters': showHosters,
    }
