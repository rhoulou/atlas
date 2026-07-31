# -*- coding: utf-8 -*-

import re
import json
import xbmc
import xbmcgui

from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.comaddon import siteManager, addon

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/sites/logos/xhamsterlive.png'

SITE_IDENTIFIER = 'xhamsterlive'
SITE_NAME = 'xHamsterLive'
SITE_DESC = 'live cams'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER).rstrip('/')

API_BASE = URL_MAIN + '/api/front/models?limit=80&sortBy=trending&offset=0&primaryTag='

CHAT_FEMALE = (API_BASE + 'girls', 'showRooms')
CHAT_COUPLES = (API_BASE + 'couples', 'showRooms')
CHAT_MALE = (API_BASE + 'men', 'showRooms')
CHAT_TRANS = (API_BASE + 'trans', 'showRooms')

URL_SEARCH = (URL_MAIN, 'showSearch')
FUNCTION_SEARCH = 'showSearch'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'


def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_SEARCH[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', CHAT_FEMALE[0])
    oOutputParameterHandler.addParameter('sCatName', 'Female')
    oGui.addDir(SITE_IDENTIFIER, 'showRooms', 'Female', icons + '/LiveTV.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', CHAT_COUPLES[0])
    oOutputParameterHandler.addParameter('sCatName', 'Couples')
    oGui.addDir(SITE_IDENTIFIER, 'showRooms', 'Couples', icons + '/LiveTV.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', CHAT_MALE[0])
    oOutputParameterHandler.addParameter('sCatName', 'Male')
    oGui.addDir(SITE_IDENTIFIER, 'showRooms', 'Male', icons + '/LiveTV.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', CHAT_TRANS[0])
    oOutputParameterHandler.addParameter('sCatName', 'Trans')
    oGui.addDir(SITE_IDENTIFIER, 'showRooms', 'Trans', icons + '/LiveTV.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        for sGender in ('girls', 'couples', 'men', 'trans'):
            sUrl = API_BASE + sGender
            showRooms(sUrl, sSearchText)
        oGui.setEndOfDirectory()
        return


def showRooms(sSearch='', sSearchText=''):
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sCatName = oInputParameterHandler.getValue('sCatName')

    if sSearch:
        sUrl = sSearch
    else:
        sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    oRequestHandler.addHeaderEntry('Accept', 'application/json')
    oRequestHandler.addHeaderEntry('Referer', URL_MAIN + '/')
    sHtmlContent = oRequestHandler.request()

    try:
        roomsData = json.loads(sHtmlContent)
    except Exception:
        oGui.setEndOfDirectory()
        return

    rooms = roomsData.get('models', [])

    if sSearchText:
        rooms = [r for r in rooms if sSearchText.lower() in r.get('username', '').lower()]

    for room in rooms:
        sUsername = room.get('username', '')
        sThumb = room.get('previewUrlThumbSmall', '')
        sViewers = room.get('viewersCount', 0)
        sCountry = room.get('country', '')
        sStatus = room.get('status', '')
        sIsNew = room.get('isNew', False)
        sId = room.get('id', '')
        sHls = 'https://edge-hls.saawsedge.com/hls/{0}/master/{0}_auto.m3u8'.format(sId)
        sIsHd = room.get('isHd', False)

        if sStatus != 'public' or not sId:
            continue

        sTitle = sUsername
        if sCountry:
            sTitle += ' [' + sCountry.upper() + ']'
        sTitle += ' (' + str(sViewers) + ')'
        if sIsNew:
            sTitle += ' [NEW]'
        if sIsHd:
            sTitle += ' [HD]'

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
        oOutputParameterHandler.addParameter('sThumb', sThumb)
        oOutputParameterHandler.addParameter('sStreamUrl', sHls)
        oOutputParameterHandler.addParameter('sUsername', sUsername)
        oOutputParameterHandler.addParameter('sViewers', str(sViewers))
        oOutputParameterHandler.addParameter('sCatName', sCatName)

        oGui.addLink(SITE_IDENTIFIER, 'showHosters', sTitle, sThumb, '', oOutputParameterHandler)

    iOffset = int(re.search(r'offset=(\d+)', sUrl).group(1)) if 'offset=' in sUrl else 0
    iTotal = roomsData.get('filteredCount', len(rooms))
    if iOffset + 80 < iTotal:
        sNextUrl = re.sub(r'offset=\d+', 'offset=' + str(iOffset + 80), sUrl)
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sNextUrl)
        if sCatName:
            oOutputParameterHandler.addParameter('sCatName', sCatName)
        oGui.addDir(SITE_IDENTIFIER, 'showRooms', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showHosters():
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')
    sStreamUrl = oInputParameterHandler.getValue('sStreamUrl')

    if not sStreamUrl:
        oGui.setEndOfDirectory()
        return

    m3u8stream = re.sub(r'_\d+p\.m3u8$', '_auto.m3u8', sStreamUrl)
    xbmc.log('XHL play m3u8=' + m3u8stream, xbmc.LOGINFO)

    item = xbmcgui.ListItem(path=m3u8stream, label=sMovieTitle)
    item.setArt({'thumb': sThumb, 'icon': 'DefaultVideo.png', 'poster': sThumb})
    item.setMimeType('application/x-mpegURL')
    item.setContentLookup(False)

    from resources.lib.comaddon import addonManager
    addonManager().enableAddon('inputstream.adaptive')

    item.setProperty('inputstream', 'inputstream.adaptive')
    item.setProperty('inputstream.adaptive.manifest_type', 'hls')
    item.setProperty('inputstream.adaptive.manifest_headers',
        'User-Agent={}&Referer={}'.format(USER_AGENT, URL_MAIN + '/'))

    xbmc.Player().play(m3u8stream, item)
