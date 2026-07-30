# -*- coding: utf-8 -*-

import re
import json
import gzip
import zlib
import xbmc
import xbmcgui

from urllib.request import Request, urlopen as _uopen
from urllib.parse import urlencode
from urllib.error import HTTPError as _HTTPError

from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.comaddon import siteManager, addon, VSlog

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/sites/logos/bongacams.png'

SITE_IDENTIFIER = 'bongacams'
SITE_NAME = 'BongaCams'
SITE_DESC = 'live cams'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER).rstrip('/')

BC_FEMALE = (URL_MAIN + '/tools/listing_v3.php?livetab=female&offset=0&limit=72', 'showRooms')
BC_COUPLES = (URL_MAIN + '/tools/listing_v3.php?livetab=couples&offset=0&limit=72', 'showRooms')
BC_MALE = (URL_MAIN + '/tools/listing_v3.php?livetab=male&offset=0&limit=72', 'showRooms')
BC_TRANS = (URL_MAIN + '/tools/listing_v3.php?livetab=transsexual&offset=0&limit=72', 'showRooms')

URL_SEARCH = (URL_MAIN, 'showSearch')
FUNCTION_SEARCH = 'showSearch'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'


def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_SEARCH[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', BC_FEMALE[0])
    oOutputParameterHandler.addParameter('sCatName', 'Female')
    oGui.addDir(SITE_IDENTIFIER, 'showRooms', 'Female', icons + '/LiveTV.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', BC_COUPLES[0])
    oOutputParameterHandler.addParameter('sCatName', 'Couples')
    oGui.addDir(SITE_IDENTIFIER, 'showRooms', 'Couples', icons + '/LiveTV.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', BC_MALE[0])
    oOutputParameterHandler.addParameter('sCatName', 'Male')
    oGui.addDir(SITE_IDENTIFIER, 'showRooms', 'Male', icons + '/LiveTV.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', BC_TRANS[0])
    oOutputParameterHandler.addParameter('sCatName', 'Trans')
    oGui.addDir(SITE_IDENTIFIER, 'showRooms', 'Trans', icons + '/LiveTV.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = URL_MAIN + '/tools/listing_v3.php?livetab=all&offset=0&limit=72&model_search%5Bdisplay_name%5D%5Btext%5D=' + sSearchText
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

    hdr = {
        'User-Agent': USER_AGENT,
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': URL_MAIN + '/',
    }
    try:
        req = Request(sUrl, headers=hdr)
        resp = _uopen(req, timeout=15)
        raw = _read_body(resp)
        sHtmlContent = raw.decode('utf-8', 'replace')
    except Exception:
        oGui.setEndOfDirectory()
        return

    try:
        roomsData = json.loads(sHtmlContent)
    except Exception:
        oGui.setEndOfDirectory()
        return

    models = roomsData.get('models', [])

    for model in models:
        sUsername = model.get('username', '')
        sDisplayName = model.get('display_name', sUsername)
        sGender = model.get('gender', '')
        sViewers = model.get('viewers', 0)
        sRoom = model.get('room', '')
        sThumbRaw = model.get('thumb_image', '')
        sVq = model.get('vq', '')
        sIsTop = model.get('is_top', False)

        if sThumbRaw:
            sThumb = 'https:' + sThumbRaw.replace('{ext}', 'jpg')
        else:
            sThumb = ''

        if sRoom != 'public':
            continue

        sTitle = sDisplayName
        if sVq and '1080' in sVq:
            sTitle += ' [HD]'
        sTitle += ' (' + str(sViewers) + ')'
        if sIsTop:
            sTitle += ' [TOP]'

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
        oOutputParameterHandler.addParameter('sThumb', sThumb)
        oOutputParameterHandler.addParameter('sUsername', sUsername)
        oOutputParameterHandler.addParameter('sViewers', str(sViewers))

        oGui.addLink(SITE_IDENTIFIER, 'showHosters', sTitle, sThumb, '', oOutputParameterHandler)

    iOffset = int(re.search(r'offset=(\d+)', sUrl).group(1)) if 'offset=' in sUrl else 0
    iTotal = roomsData.get('total_count', len(models))
    if iOffset + 72 < iTotal:
        sNextUrl = re.sub(r'offset=\d+', 'offset=' + str(iOffset + 72), sUrl)
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sNextUrl)
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

    xbmc.log('BC showHosters user=' + repr(sUsername), xbmc.LOGINFO)

    if not sUsername:
        xbmc.log('BC no username, exit', xbmc.LOGINFO)
        oGui.setEndOfDirectory()
        return

    amf_url = URL_MAIN + '/tools/amf.php'
    post_data = 'method=getRoomData&args%5B%5D=' + sUsername + '&args%5B%5D=false'
    hdr = {
        'User-Agent': USER_AGENT,
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': URL_MAIN + '/' + sUsername,
    }

    m3u8stream = None
    try:
        req = Request(amf_url, data=post_data.encode('utf-8'), headers=hdr)
        resp = _uopen(req, timeout=15)
        raw = _read_body(resp)
        resp_data = json.loads(raw.decode('utf-8', 'replace'))
        xbmc.log('BC AMF status=' + str(resp_data.get('status')) + ' showType=' + str(resp_data.get('performerData', {}).get('showType', '')), xbmc.LOGINFO)

        if resp_data.get('status') == 'success':
            showType = resp_data.get('performerData', {}).get('showType', '')
            videoServerUrl = resp_data.get('localData', {}).get('videoServerUrl', '')
            if showType == 'public' and videoServerUrl:
                proto = 'https:' if videoServerUrl.startswith('//') else ''
                m3u8stream = proto + videoServerUrl + '/hls/stream_' + sUsername + '/playlist.m3u8'
                xbmc.log('BC m3u8stream OK', xbmc.LOGINFO)
            else:
                xbmc.log('BC not public or no server url', xbmc.LOGINFO)
    except Exception as e:
        xbmc.log('BC AMF FAIL: ' + str(e), xbmc.LOGERROR)

    if not m3u8stream:
        xbmc.log('BC m3u8stream is None, exit', xbmc.LOGINFO)
        oGui.setEndOfDirectory()
        return

    item = xbmcgui.ListItem(path=m3u8stream, label=sMovieTitle)
    item.setArt({'thumb': sThumb, 'icon': 'DefaultVideo.png', 'poster': sThumb})
    item.setMimeType('application/x-mpegURL')
    item.setContentLookup(False)

    from resources.lib.comaddon import addonManager
    addonManager().enableAddon('inputstream.ffmpegdirect')

    item.setProperty('inputstream', 'inputstream.ffmpegdirect')
    item.setProperty('inputstream.ffmpegdirect.manifest_type', 'hls')
    item.setProperty('inputstream.ffmpegdirect.manifest_headers',
        'User-Agent={}&Referer={}'.format(USER_AGENT, URL_MAIN + '/'))

    xbmc.log('BC playing m3u8=' + m3u8stream[:80], xbmc.LOGINFO)

    xbmc.Player().play(m3u8stream, item)
    xbmc.log('BC play done', xbmc.LOGINFO)
