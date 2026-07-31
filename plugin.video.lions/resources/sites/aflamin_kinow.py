# -*- coding: utf-8 -*-
import re
import time
import requests

from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.comaddon import VSlog, siteManager, addon

PER_PAGE = 15

DEFAULT_API_URL = 'https://platform-353.kinow.io/graphql'

CATEGORY_ICONS = {
    'دراما': '/TVShows.png',
    'كوميديا': '/Movies.png',
    'عائلي': '/family.png',
    'كلاسيكية': '/MoviesClassic.png',
    'وثائقية': '/Documentary.png',
    'موسيقية': '/music.png',
    'عربية': '/ARABIC.png',
    'دولي': '/MoviesEnglish.png',
    'تعليم': '/Movies.png',
    'خطوات أولى': '/Kids.png',
    'رعب': '/Movies.png',
    'بوليسية': '/Movies.png',
    'قصيرة': '/Movies.png',
    'drames': '/TVShows.png',
    'comédies': '/Movies.png',
    'famille': '/family.png',
    'classiques': '/MoviesClassic.png',
    'documentaires': '/Documentary.png',
    'musicaux': '/music.png',
    'arabes': '/ARABIC.png',
    'monde': '/MoviesEnglish.png',
    'horreur': '/Movies.png',
    'policiers': '/Movies.png',
    'courts': '/Movies.png',
}

DEFAULT_CATEGORY_ICON = '/Movies.png'


def buildSite(sSiteIdentifier, sSiteName, sLang, sSiteDesc):
    URL_MAIN = siteManager().getUrlMain(sSiteIdentifier)
    icons = addon().getSetting('defaultIcons')

    def _getApiUrl():
        if not hasattr(_getApiUrl, 'url'):
            sApiUrl = DEFAULT_API_URL
            try:
                oResponse = requests.get(URL_MAIN, timeout=20,
                                         headers={'User-Agent': 'Mozilla/5.0'})
                oMatch = re.search(r'"apiUrl":"(https://[^"]+)"', oResponse.text)
                if oMatch:
                    sApiUrl = oMatch.group(1)
            except Exception as e:
                VSlog('aflamin: api url lookup failed (' + str(e) + ')')
            _getApiUrl.url = sApiUrl
        return _getApiUrl.url

    def _apiQuery(sQuery, dVariables=None):
        sApiUrl = _getApiUrl()
        dPayload = {'query': sQuery, 'variables': dVariables or {}}
        oHeaders = {'User-Agent': 'Mozilla/5.0', 'accept-language': sLang}

        aData = None
        for _ in range(2):
            try:
                oResponse = requests.post(sApiUrl, json=dPayload, timeout=30, headers=oHeaders)
                aData = oResponse.json()
                if aData and 'data' in aData:
                    return aData
            except Exception:
                pass
            time.sleep(1)

        return aData or {}

    def _getCategoryIcon(sName):
        for sKey, sIcon in CATEGORY_ICONS.items():
            if sKey in sName:
                return icons + sIcon
        return icons + DEFAULT_CATEGORY_ICON

    def load():
        oGui = cGui()
        oOutputParameterHandler = cOutputParameterHandler()

        try:
            sQuery = ('query { cms { categories(query: "parent: 0") { items { id name '
                      'children(perPage: 100) { items { id name } } } } } }')
            aData = _apiQuery(sQuery)

            aCategories = []
            for oRoot in aData['data']['cms']['categories']['items']:
                aCategories = oRoot.get('children', {}).get('items', [])
                if aCategories:
                    break

            for oCat in aCategories:
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', oCat['id'])
                oGui.addDir(sSiteIdentifier, 'showCategory', oCat['name'],
                            _getCategoryIcon(oCat['name']), oOutputParameterHandler)
        except Exception as e:
            VSlog('aflamin: load failed (' + str(e) + ')')
            oGui.addText(sSiteIdentifier, '[COLOR red]Error loading catalogue[/COLOR]')

        oGui.setEndOfDirectory()

    def showCategory():
        oGui = cGui()
        oInputParameterHandler = cInputParameterHandler()
        sCatId = oInputParameterHandler.getValue('siteUrl')
        sPage = oInputParameterHandler.getValue('sPage')
        iPage = int(sPage) if sPage else 1

        oOutputParameterHandler = cOutputParameterHandler()
        sQuery = ('query GET($ids: [ID!], $pg: Int, $pp: Int) { cms { categories(includeIds: $ids) { '
                  'items { id name products(page: $pg, perPage: $pp) { pagination { page lastPage total } '
                  'items { id name dateFrom description images { source } metadata { name value } } } } } } }')
        dVars = {'ids': [sCatId], 'pg': iPage, 'pp': PER_PAGE}

        try:
            aData = _apiQuery(sQuery, dVars)
            oCat = aData['data']['cms']['categories']['items'][0]
            oProducts = oCat['products']
            iLastPage = oProducts['pagination']['lastPage']

            for oProduct in oProducts['items']:
                sTitle = oProduct['name']
                sThumb = _pickCover(oProduct.get('images', []))
                sDesc = oProduct.get('description') or ''

                sYear = _pickYear(oProduct.get('dateFrom'))
                if sYear:
                    sLabel = '%s (%s)' % (sTitle, sYear)
                else:
                    sLabel = sTitle

                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', oProduct['id'])
                oOutputParameterHandler.addParameter('sTitle', sTitle)
                oOutputParameterHandler.addParameter('sYear', sYear)
                oOutputParameterHandler.addParameter('sThumb', sThumb)

                oGui.addDrama(sSiteIdentifier, 'searchDrama', sLabel,
                              sThumb if sThumb else icons + '/Movies.png', sThumb, sDesc,
                              oOutputParameterHandler)

            if iPage < iLastPage:
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sCatId)
                oOutputParameterHandler.addParameter('sPage', str(iPage + 1))
                oGui.addDir(sSiteIdentifier, 'showCategory', '[COLOR teal]Next >>>[/COLOR]',
                            icons + '/Next.png', oOutputParameterHandler)
        except Exception as e:
            VSlog('aflamin: showCategory failed (' + str(e) + ')')
            oGui.addText(sSiteIdentifier, '[COLOR red]Error loading category[/COLOR]')

        oGui.setEndOfDirectory()

    def searchDrama():
        oInputParameterHandler = cInputParameterHandler()
        sTitle = oInputParameterHandler.getValue('sTitle')
        sYear = oInputParameterHandler.getValue('sYear')

        if not sTitle:
            return False

        sSearchText = sTitle
        if sYear:
            sSearchText = '%s %s' % (sTitle, sYear)

        from resources.lib.search import cSearch
        cSearch().searchGlobal(sSearchText, '9')

        return True

    def _pickCover(aImages):
        sCover = ''
        for oImage in aImages:
            sSource = oImage.get('source', '')
            if not sSource:
                continue
            if '-cover_' in sSource or '-player_' in sSource:
                return sSource
            if not sCover:
                sCover = sSource
        return sCover

    def _pickYear(sDateFrom):
        if sDateFrom and len(sDateFrom) >= 4:
            sYear = sDateFrom[:4]
            if sYear.isdigit() and 1900 < int(sYear) <= 2100:
                return sYear
        return ''

    return {
        'SITE_IDENTIFIER': sSiteIdentifier,
        'SITE_NAME': sSiteName,
        'SITE_DESC': sSiteDesc,
        'load': load,
        'showCategory': showCategory,
        'searchDrama': searchDrama,
    }
