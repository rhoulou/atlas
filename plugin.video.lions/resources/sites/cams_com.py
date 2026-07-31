# -*- coding: utf-8 -*-

import re
import json
import xbmc
import xbmcgui

from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.comaddon import siteManager, addon, dialog

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/art/sites/cams.png'

SITE_IDENTIFIER = 'cams_com'
SITE_NAME = 'cams.com'
SITE_DESC = 'live cams'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER).rstrip('/')

CHAT_FEMALE = (URL_MAIN, 'showRooms')
CHAT_MALE = (URL_MAIN, 'showRooms')
CHAT_TRANS = (URL_MAIN, 'showRooms')

URL_SEARCH = (URL_MAIN, 'showSearch')
FUNCTION_SEARCH = 'showSearch'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'

GENDER_TRANS = ('TS', 'T')


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
        showRooms(URL_MAIN, sSearchText)
        oGui.setEndOfDirectory()


def showRooms(sSearch='', sSearchText=''):
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sCatName = oInputParameterHandler.getValue('sCatName')

    if sSearch:
        sUrl = sSearch
    else:
        sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    oRequestHandler.addHeaderEntry('User-Agent', USER_AGENT)
    oRequestHandler.addHeaderEntry('Referer', URL_MAIN + '/')
    sHtmlContent = oRequestHandler.request()

    if not sHtmlContent:
        oGui.setEndOfDirectory()
        return

    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', sHtmlContent, re.DOTALL)
    if not m:
        oGui.setEndOfDirectory()
        return

    try:
        d = json.loads(m.group(1))
        won = d['props']['pageProps']['initialData']['wonStore']['compressedWonResponse']
        mapping = won['mapping']
        rooms = [dict(zip(mapping, raw)) for raw in won['models']]
    except Exception:
        oGui.setEndOfDirectory()
        return

    if sSearchText:
        rooms = [r for r in rooms if sSearchText.lower() in r.get('screen_name', '').lower()]

    if sCatName == 'Female':
        rooms = [r for r in rooms if r.get('gender', '') == 'F']
    elif sCatName == 'Male':
        rooms = [r for r in rooms if r.get('gender', '') == 'M']
    elif sCatName == 'Trans':
        rooms = [r for r in rooms if r.get('gender', '') in GENDER_TRANS]

    for room in rooms:
        sUsername = room.get('screen_name', '')
        if not sUsername:
            continue
        if str(room.get('chat_type', '')) != '1':
            continue

        sTitle = sUsername
        sThumb = 'https://dynimages.securedataimages.com/unsigned/rs:fill:640::0/g:no/plain/https%3A%2F%2Fimages4.streamray.com%2Fimages%2Fstreamray%2Fstreams%2F%s_640.gif@webp' % sUsername.lower()
        sStreamUrl = 'https://camshls.cams.com/cdn-%s.m3u8' % sUsername.lower()

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
        oOutputParameterHandler.addParameter('sThumb', sThumb)
        oOutputParameterHandler.addParameter('sStreamUrl', sStreamUrl)
        oOutputParameterHandler.addParameter('sUsername', sUsername)
        oOutputParameterHandler.addParameter('sCatName', sCatName)

        oGui.addLink(SITE_IDENTIFIER, 'showHosters', sTitle, sThumb, '', oOutputParameterHandler)

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

    oRequestHandler = cRequestHandler(sStreamUrl)
    oRequestHandler.addHeaderEntry('User-Agent', USER_AGENT)
    oRequestHandler.addHeaderEntry('Referer', URL_MAIN + '/')
    sContent = oRequestHandler.request()
    if not sContent or not sContent.strip().startswith('#EXTM3U'):
        dialog().VSerror('Stream unavailable')
        oGui.setEndOfDirectory()
        return

    xbmc.log('SC play m3u8=' + sStreamUrl, xbmc.LOGINFO)

    item = xbmcgui.ListItem(path=sStreamUrl, label=sMovieTitle)
    item.setArt({'thumb': sThumb, 'icon': 'DefaultVideo.png', 'poster': sThumb})
    item.setMimeType('application/x-mpegURL')
    item.setContentLookup(False)

    from resources.lib.comaddon import addonManager
    addonManager().enableAddon('inputstream.adaptive')

    item.setProperty('inputstream', 'inputstream.adaptive')
    item.setProperty('inputstream.adaptive.manifest_type', 'hls')
    item.setProperty('inputstream.adaptive.manifest_headers',
        'User-Agent={}&Referer={}'.format(USER_AGENT, URL_MAIN + '/'))

    xbmc.Player().play(sStreamUrl, item)
