# -*- coding: utf-8 -*-
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.comaddon import addon


def buildSite(sSiteIdentifier, sSiteName, sLang, sSiteDesc):
    icons = addon().getSetting('defaultIcons')
    LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/' + sSiteIdentifier + '.png'

    URL_MAIN = 'https://weyyak.com/'
    URL_SEARCH = ('', 'showSearch')
    URL_SEARCH_DRAMAS = URL_SEARCH
    FUNCTION_SEARCH = 'showSearch'

    def load():
        oGui = cGui()
        oGui.addText(sSiteIdentifier, '[COLOR gray]Coming soon[/COLOR]')
        oGui.setEndOfDirectory()

    def showSearch(sSearchText=''):
        oGui = cGui()
        oGui.addText(sSiteIdentifier, '[COLOR gray]Coming soon[/COLOR]')
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
        'showSearch': showSearch,
    }
