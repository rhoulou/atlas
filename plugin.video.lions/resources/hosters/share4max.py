#coding: utf-8
import json
import re
from resources.lib.handler.requestHandler import cRequestHandler
from resources.hosters.hoster import iHoster

SUPPORTED_DRIVERS = ['voe', 'mp4upload', 'lulustream', 'doodstream', 'krakenfiles', 'vidmoly']

class cHoster(iHoster):

    def __init__(self):
        iHoster.__init__(self, 'share4max', 'Share4Max')

    def isDownloadable(self):
        return False

    def setUrl(self, url):
        self._url = str(url)

    def _getMediaLinkForGuest(self):
        oRequest = cRequestHandler(self._url)
        sHtmlContent = oRequest.request()

        match = re.search(r'data-page="app"[^>]*type="application/json">(.*?)</script>', sHtmlContent, re.DOTALL)
        if not match:
            return False, False

        try:
            page_data = json.loads(match.group(1))
        except Exception:
            return False, False

        version = page_data.get('version', '')
        if not version:
            return False, False

        oRequest2 = cRequestHandler(self._url)
        oRequest2.addHeaderEntry('X-Inertia', 'true')
        oRequest2.addHeaderEntry('X-Inertia-Version', version)
        oRequest2.addHeaderEntry('X-Inertia-Partial-Data', 'streams')
        oRequest2.addHeaderEntry('X-Inertia-Partial-Component', 'files/mirror/video')
        oRequest2.addHeaderEntry('Accept', 'application/json')
        sHtmlContent2 = oRequest2.request()

        try:
            data = json.loads(sHtmlContent2)
        except Exception:
            return False, False

        streams = data.get('props', {}).get('streams', {})
        if streams.get('status') != 'success':
            return False, False

        stream_list = streams.get('data', [])
        if not stream_list:
            return False, False

        for stream in stream_list:
            for mirror in stream.get('mirrors', []):
                driver = mirror.get('driver', '')
                link = mirror.get('link', '')
                if not link:
                    continue
                if link.startswith('//'):
                    link = 'https:' + link
                if driver in SUPPORTED_DRIVERS:
                    return True, link

        for stream in stream_list:
            for mirror in stream.get('mirrors', []):
                link = mirror.get('link', '')
                if link:
                    if link.startswith('//'):
                        link = 'https:' + link
                    return True, link

        return False, False
