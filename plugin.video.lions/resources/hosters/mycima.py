#-*- coding: utf-8 -*-
from resources.lib.handler.requestHandler import cRequestHandler
from resources.hosters.hoster import iHoster
from resources.lib.comaddon import VSlog
import re
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0'


class cHoster(iHoster):

    def __init__(self):
        iHoster.__init__(self, 'mycima', 'wecima')

    def _getMediaLinkForGuest(self):
        VSlog(self._url)

        sUrl = self._url.split('|')[0]

        oRequestHandler = cRequestHandler(sUrl)
        oRequestHandler.addHeaderEntry('User-Agent', UA)
        oRequestHandler.addHeaderEntry('Referer', 'https://wecima.gold/')
        sHtmlContent = oRequestHandler.request()

        m = re.search(r'const videoUrl\s*=\s*"([^"]+)"', sHtmlContent)
        if m:
            api_call = m.group(1).replace('&#038;', '&')

            if '.m3u8' in api_call or 'master.txt' in api_call:
                api_call = api_call + '|User-Agent=' + UA + '&Referer=https://akhbarworld.online/'

            if api_call:
                return True, api_call

        return False, False
