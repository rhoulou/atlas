# -*- coding: utf-8 -*-

import re
import json
import sys
import gzip
import zlib
import xbmc
import xbmcgui

from urllib.request import Request, urlopen as _uopen
from urllib.parse import urlencode, urljoin as _urljoin
from urllib.error import HTTPError as _HTTPError

from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.comaddon import siteManager, addon, VSlog

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/sites/logos/chaturbate.png'

SITE_IDENTIFIER = 'chaturbate'
SITE_NAME = 'Chaturbate'
SITE_DESC = 'live cams'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER).rstrip('/')

CHAT_FEMALE = (URL_MAIN + '/api/ts/roomlist/room-list/?genders=f&limit=100&offset=0', 'showRooms')
CHAT_COUPLES = (URL_MAIN + '/api/ts/roomlist/room-list/?genders=c&limit=100&offset=0', 'showRooms')
CHAT_MALE = (URL_MAIN + '/api/ts/roomlist/room-list/?genders=m&limit=100&offset=0', 'showRooms')
CHAT_TRANS = (URL_MAIN + '/api/ts/roomlist/room-list/?genders=t&limit=100&offset=0', 'showRooms')

TAG_URL = URL_MAIN + '/api/ts/hashtags/top_tags/?count=100'

URL_SEARCH = ('', 'showSearch')
FUNCTION_SEARCH = 'showSearch'

USER_AGENT_IPAD = 'Mozilla/5.0 (iPad; CPU OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B410 Safari/600.1.4'


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

    oRequestHandler = cRequestHandler(TAG_URL)
    oRequestHandler.addHeaderEntry('Referer', URL_MAIN + '/')
    sHtmlContent = oRequestHandler.request()

    try:
        tagsData = json.loads(sHtmlContent)
        allTags = tagsData.get('all_tags', [])
    except Exception:
        allTags = ['young', 'latin', 'ebony', 'asian', 'milf', 'teen', 'anal',
                    'squirt', 'bigtits', 'smalltits', 'hairy', 'shaved', 'colombian',
                    'german']

    for tag in allTags[:14]:
        tagUrl = URL_MAIN + '/api/ts/roomlist/room-list/?genders=f&limit=100&offset=0&tag=' + tag
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', tagUrl)
        oOutputParameterHandler.addParameter('sTag', tag)
        oOutputParameterHandler.addParameter('sCatName', '#' + tag)
        oGui.addDir(SITE_IDENTIFIER, 'showRooms', '#' + tag, icons + '/LiveTV.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showSearch(sSearchText=''):
    oGui = cGui()
    if not sSearchText:
        sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = URL_MAIN + '/api/ts/roomlist/room-list/?genders=f&limit=100&offset=0'
        showRooms(sUrl, sSearchText)
        oGui.setEndOfDirectory()
        return


def showRooms(sSearch='', sSearchText=''):
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sTag = oInputParameterHandler.getValue('sTag')
    sCatName = oInputParameterHandler.getValue('sCatName')

    if sSearch:
        sUrl = sSearch
    else:
        sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    oRequestHandler.addHeaderEntry('Referer', URL_MAIN + '/')
    sHtmlContent = oRequestHandler.request()

    try:
        roomsData = json.loads(sHtmlContent)
    except Exception:
        oGui.setEndOfDirectory()
        return

    rooms = roomsData.get('rooms', [])

    if sTag:
        rooms = [r for r in rooms if sTag in r.get('tags', [])]

    if sSearchText:
        rooms = [r for r in rooms if sSearchText.lower() in r.get('username', '').lower()]

    for room in rooms:
        sUsername = room.get('username', '')
        sThumb = room.get('img', '')
        sViewers = room.get('num_users', 0)
        sCountry = room.get('country', '').upper()
        sGender = room.get('gender', '')
        sSubject = room.get('subject', '').strip()
        sIsNew = room.get('is_new', False)

        sTitle = sUsername
        if sCountry:
            sTitle += ' [' + sCountry + ']'
        sTitle += ' (' + str(sViewers) + ')'
        if sIsNew:
            sTitle += ' [NEW]'

        sDesc = sSubject if sSubject else sCatName

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
        oOutputParameterHandler.addParameter('sThumb', sThumb)
        oOutputParameterHandler.addParameter('sUsername', sUsername)
        oOutputParameterHandler.addParameter('sViewers', str(sViewers))

        oGui.addLink(SITE_IDENTIFIER, 'showHosters', sTitle, sThumb, '', oOutputParameterHandler)

    iOffset = int(re.search(r'offset=(\d+)', sUrl).group(1)) if 'offset=' in sUrl else 0
    iTotal = roomsData.get('total_count', len(rooms))
    if iOffset + 100 < iTotal:
        sNextUrl = re.sub(r'offset=\d+', 'offset=' + str(iOffset + 100), sUrl)
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sNextUrl)
        if sTag:
            oOutputParameterHandler.addParameter('sTag', sTag)
        if sCatName:
            oOutputParameterHandler.addParameter('sCatName', sCatName)
        oGui.addDir(SITE_IDENTIFIER, 'showRooms', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def _read_body(resp):
    raw = resp.read()
    ce = (resp.headers.get('Content-Encoding') or '').lower()
    if ce == 'gzip' or raw[:2] == b'\x1f\x8b':
        try:
            raw = gzip.decompress(raw)
        except Exception:
            pass
    elif ce == 'deflate':
        try:
            raw = zlib.decompress(raw)
        except Exception:
            try:
                raw = zlib.decompress(raw, -zlib.MAX_WBITS)
            except Exception:
                pass
    return raw


def showHosters():
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')
    sUsername = oInputParameterHandler.getValue('sUsername')

    xbmc.log('CB showHosters user=' + repr(sUsername), xbmc.LOGINFO)

    if not sUsername:
        xbmc.log('CB no username, exit', xbmc.LOGINFO)
        oGui.setEndOfDirectory()
        return

    slug = sUsername.strip('/')
    ajax_url = URL_MAIN + '/get_edge_hls_url_ajax/'
    hdr = {
        'User-Agent': USER_AGENT_IPAD,
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': URL_MAIN + '/' + slug + '/',
    }
    post_data = urlencode({'room_slug': slug, 'bandwidth': 'high'}).encode('utf-8')

    m3u8stream = None
    try:
        req = Request(ajax_url, data=post_data, headers=hdr)
        resp = _uopen(req, timeout=15)
        raw = _read_body(resp)
        resp_data = json.loads(raw.decode('utf-8', 'replace'))
        xbmc.log('CB AJAX resp keys=' + str(list(resp_data.keys())) + ' room_status=' + str(resp_data.get('room_status')), xbmc.LOGINFO)
        if resp_data.get('room_status') == 'public' and resp_data.get('url'):
            m3u8stream = resp_data['url']
            xbmc.log('CB m3u8stream OK len=' + str(len(m3u8stream)), xbmc.LOGINFO)
        else:
            xbmc.log('CB no url or not public', xbmc.LOGINFO)
    except Exception as e:
        xbmc.log('CB AJAX FAIL: ' + str(e), xbmc.LOGERROR)

    if not m3u8stream:
        xbmc.log('CB m3u8stream is None, exit', xbmc.LOGINFO)
        oGui.setEndOfDirectory()
        return

    item = xbmcgui.ListItem(path=m3u8stream, label=sMovieTitle)
    item.setArt({'thumb': sThumb, 'icon': 'DefaultVideo.png', 'poster': sThumb})
    item.setMimeType('application/x-mpegURL')
    item.setContentLookup(False)

    from resources.lib.comaddon import addonManager
    addonManager().enableAddon('inputstream.adaptive')

    item.setProperty('inputstream', 'inputstream.adaptive')
    item.setProperty('inputstream.adaptive.manifest_type', 'hls')
    item.setProperty('inputstream.adaptive.manifest_headers',
        'User-Agent={}&Referer={}'.format(USER_AGENT_IPAD, URL_MAIN + '/'))

    xbmc.log('CB playing m3u8=' + m3u8stream[:80], xbmc.LOGINFO)

    xbmc.Player().play(m3u8stream, item)
    xbmc.log('CB play done', xbmc.LOGINFO)
