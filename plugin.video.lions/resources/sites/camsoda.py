# -*- coding: utf-8 -*-

import re
import json
import random
import gzip
import zlib
import threading
import xbmc
import xbmcgui

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen as _uopen
from urllib.parse import quote as UrlEncode, urlparse
from urllib.error import HTTPError as _HTTPError

from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.comaddon import siteManager, addon, VSlog

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/sites/logos/camsoda.png'

SITE_IDENTIFIER = 'camsoda'
SITE_NAME = 'CamSoda'
SITE_DESC = 'live cams'

URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER).rstrip('/')

CS_FEMALE = (URL_MAIN + '/api/v1/browse/react?gender-hide=m,t', 'showRooms', 'f')
CS_COUPLES = (URL_MAIN + '/api/v1/browse/react?gender-hide=m,f,t', 'showRooms', 'c')
CS_MALE = (URL_MAIN + '/api/v1/browse/react?gender-hide=f,c,t', 'showRooms', 'm')
CS_TRANS = (URL_MAIN + '/api/v1/browse/react?gender-hide=m,f,c', 'showRooms', 't')

URL_SEARCH = (URL_MAIN, 'showSearch')
FUNCTION_SEARCH = 'showSearch'

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0'

CDN_ORIGIN = 'https://streaming-edge-front.livemediahost.com'

PAGE_SIZE = 100


def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_SEARCH[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Search', LOGO, oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', CS_FEMALE[0])
    oOutputParameterHandler.addParameter('sGender', 'f')
    oOutputParameterHandler.addParameter('sCatName', 'Female')
    oGui.addDir(SITE_IDENTIFIER, 'showRooms', 'Female', icons + '/LiveTV.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', CS_COUPLES[0])
    oOutputParameterHandler.addParameter('sGender', 'c')
    oOutputParameterHandler.addParameter('sCatName', 'Couples')
    oGui.addDir(SITE_IDENTIFIER, 'showRooms', 'Couples', icons + '/LiveTV.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', CS_MALE[0])
    oOutputParameterHandler.addParameter('sGender', 'm')
    oOutputParameterHandler.addParameter('sCatName', 'Male')
    oGui.addDir(SITE_IDENTIFIER, 'showRooms', 'Male', icons + '/LiveTV.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', CS_TRANS[0])
    oOutputParameterHandler.addParameter('sGender', 't')
    oOutputParameterHandler.addParameter('sCatName', 'Trans')
    oGui.addDir(SITE_IDENTIFIER, 'showRooms', 'Trans', icons + '/LiveTV.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', URL_MAIN)
        oOutputParameterHandler.addParameter('sSearchText', sSearchText)
        oOutputParameterHandler.addParameter('sGender', 'all')
        showRooms(sSearchText=sSearchText)
        oGui.setEndOfDirectory()
        return


def _fetch_json(url):
    hdr = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/json, text/plain, */*',
        'Referer': URL_MAIN + '/',
    }
    req = Request(url, headers=hdr)
    resp = _uopen(req, timeout=15)
    raw = _read_body(resp)
    return json.loads(raw.decode('utf-8', 'replace'))


def _build_hls_url(edge_url, stream_name):
    if not edge_url or not stream_name:
        return None
    edge_host = edge_url.replace('.livemediahost.com', '')
    return CDN_ORIGIN + '/' + edge_host + '/' + stream_name + '_v1/index.ll.m3u8'


def showRooms(sSearchText=''):
    oGui = cGui()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sGender = oInputParameterHandler.getValue('sGender')
    sPage = oInputParameterHandler.getValue('sPage')
    iPage = int(sPage) if sPage else 0
    sCatName = oInputParameterHandler.getValue('sCatName')

    if not sSearchText:
        sSearchText = oInputParameterHandler.getValue('sSearchText')

    isSearch = bool(sSearchText)

    filtered = []

    try:
        if isSearch:
            search_url = URL_MAIN + '/api/v1/browse/autocomplete?s=' + UrlEncode(sSearchText)
            data = _fetch_json(search_url)
            online_users = [r.get('username', '') for r in data.get('results', []) if r.get('status') == 'online']
            react_url = URL_MAIN + '/api/v1/browse/react?p=' + str(iPage + 1)
            if sGender and sGender != 'all':
                hide_map = {'f': 'm,t', 'm': 'f,c,t', 'c': 'm,f,t', 't': 'm,f,c'}
                gh = hide_map.get(sGender)
                if gh:
                    react_url += '&gender-hide=' + gh
            react_data = _fetch_json(react_url)
            for u in react_data.get('userList', []):
                if u.get('username') not in online_users:
                    continue
                if not u.get('streamEdgeUrl') or not u.get('streamName'):
                    continue
                filtered.append({
                    'username': u.get('username', ''),
                    'display_name': u.get('displayName', u.get('username', '')),
                    'viewers': u.get('connectionCount', 0),
                    'thumb': u.get('thumbUrl', ''),
                    'poster': u.get('thumbUrl', '').replace('/thumbs/', '/stills/').replace('.jpg?', '_raw.jpg?'),
                    'hls_url': _build_hls_url(u.get('streamEdgeUrl', ''), u.get('streamName', '')),
                })
        else:
            react_url = sUrl
            if iPage > 0:
                sep = '&' if '?' in react_url else '?'
                react_url += sep + 'p=' + str(iPage + 1)
            data = _fetch_json(react_url)
            for u in data.get('userList', []):
                if not u.get('streamEdgeUrl') or not u.get('streamName'):
                    continue
                filtered.append({
                    'username': u.get('username', ''),
                    'display_name': u.get('displayName', u.get('username', '')),
                    'viewers': u.get('connectionCount', 0),
                    'thumb': u.get('thumbUrl', ''),
                    'poster': u.get('thumbUrl', '').replace('/thumbs/', '/stills/').replace('.jpg?', '_raw.jpg?'),
                    'hls_url': _build_hls_url(u.get('streamEdgeUrl', ''), u.get('streamName', '')),
                })
    except Exception as e:
        xbmc.log('CS showRooms FAIL: ' + str(e), xbmc.LOGERROR)
        oGui.setEndOfDirectory()
        return

    start = 0 if isSearch else 0
    end = PAGE_SIZE * (iPage + 1) if not isSearch else len(filtered)
    page_items = filtered[start:end] if not isSearch else filtered

    for r in page_items:
        sTitle = r['display_name']
        sTitle += ' (' + str(r['viewers']) + ')'

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oOutputParameterHandler.addParameter('sMovieTitle', r['display_name'])
        oOutputParameterHandler.addParameter('sThumb', r['thumb'])
        oOutputParameterHandler.addParameter('sPoster', r['poster'])
        oOutputParameterHandler.addParameter('sUsername', r['username'])
        oOutputParameterHandler.addParameter('sViewers', str(r['viewers']))
        oOutputParameterHandler.addParameter('sHlsUrl', r.get('hls_url', ''))

        oGui.addLink(SITE_IDENTIFIER, 'showHosters', sTitle, r['thumb'], '', oOutputParameterHandler)

    if not isSearch:
        data_count = len(filtered)
        if data_count >= PAGE_SIZE:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl)
            oOutputParameterHandler.addParameter('sPage', str(iPage + 1))
            if sGender:
                oOutputParameterHandler.addParameter('sGender', sGender)
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
    sPoster = oInputParameterHandler.getValue('sPoster')
    sUsername = oInputParameterHandler.getValue('sUsername')
    sHlsUrl = oInputParameterHandler.getValue('sHlsUrl')

    xbmc.log('CS showHosters user=' + repr(sUsername), xbmc.LOGINFO)

    if not sUsername:
        xbmc.log('CS no username, exit', xbmc.LOGINFO)
        oGui.setEndOfDirectory()
        return

    m3u8stream = sHlsUrl if sHlsUrl else None

    if not m3u8stream:
        vtoken_url = URL_MAIN + '/api/v1/video/vtoken/' + sUsername + '?username=guest_' + str(random.randint(1000, 99999))
        try:
            vdata = _fetch_json(vtoken_url)
            edge_servers = vdata.get('edge_servers', [])
            stream_name = vdata.get('stream_name', '')
            token = vdata.get('token', '')
            if edge_servers and stream_name and token:
                server = edge_servers[0]
                if 'edge' in server:
                    m3u8stream = 'https://' + server + '/' + stream_name + '_v1/index.ll.m3u8?token=' + token
                else:
                    app = vdata.get('app', 'cam')
                    m3u8stream = 'https://' + server + '/' + app + '/mp4:' + stream_name + '_aac/playlist.m3u8?token=' + token
        except Exception as e:
            xbmc.log('CS vtoken FAIL: ' + str(e), xbmc.LOGERROR)

    if not m3u8stream:
        xbmc.log('CS m3u8stream is None, exit', xbmc.LOGINFO)
        oGui.setEndOfDirectory()
        return

    xbmc.log('CS m3u8stream=' + m3u8stream[:100], xbmc.LOGINFO)

    proxy_headers = {
        'User-Agent': USER_AGENT,
        'Referer': URL_MAIN + '/',
        'Origin': URL_MAIN,
    }

    class _ProxyHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            target_url = CDN_ORIGIN + self.path
            try:
                req = Request(target_url, headers=proxy_headers)
                resp = _uopen(req, timeout=15)
                data = resp.read()
                ct = resp.headers.get('Content-Type', 'application/octet-stream')

                if b'#EXTM3U' in data[:32]:
                    text = data.decode('utf-8', 'replace')
                    text = text.replace(CDN_ORIGIN, 'http://127.0.0.1:' + str(proxy_port))
                    data = text.encode('utf-8')
                    ct = 'application/vnd.apple.mpegurl'

                self.send_response(200)
                self.send_header('Content-Type', ct)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(data)
            except _HTTPError as e:
                self.send_response(e.code)
                self.end_headers()
            except Exception:
                self.send_response(502)
                self.end_headers()

        def log_message(self, *a):
            pass

    server = HTTPServer(('127.0.0.1', 0), _ProxyHandler)
    proxy_port = server.server_address[1]
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    xbmc.log('CS proxy started on 127.0.0.1:' + str(proxy_port), xbmc.LOGINFO)

    parsed = urlparse(m3u8stream)
    local_url = 'http://127.0.0.1:' + str(proxy_port) + parsed.path
    if parsed.query:
        local_url += '?' + parsed.query
    xbmc.log('CS playing local=' + local_url[:120], xbmc.LOGINFO)

    item = xbmcgui.ListItem(path=local_url, label=sMovieTitle)
    item.setArt({'thumb': sThumb, 'icon': 'DefaultVideo.png', 'poster': sPoster or sThumb})
    item.setMimeType('application/x-mpegURL')
    item.setContentLookup(False)

    xbmc.Player().play(local_url, item)
    xbmc.log('CS play done', xbmc.LOGINFO)
