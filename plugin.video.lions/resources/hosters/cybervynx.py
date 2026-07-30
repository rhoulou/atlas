#coding: utf-8
import re
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.hosters.hoster import iHoster
from resources.lib.comaddon import VSlog


class cHoster(iHoster):

    def __init__(self):
        iHoster.__init__(self, 'cybervynx', 'CyberVynx')

    def isDownloadable(self):
        return False

    def setUrl(self, url):
        self._url = str(url)

    def _getMediaLinkForGuest(self):
        VSlog(self._url)
        api_call = ''

        oRequest = cRequestHandler(self._url)
        sHtmlContent = oRequest.request()

        oParser = cParser()

        sPattern = r'(?:file|src|source)\s*[:=]\s*["\']?(https?://[^"\'<>\s]+\.(?:mp4|m3u8)[^"\'<>\s]*)'
        aResult = oParser.parse(sHtmlContent, sPattern)
        if aResult[0]:
            api_call = aResult[1][0]
            if api_call.startswith('//'):
                api_call = 'https:' + api_call
            return True, api_call + '|Referer=' + self._url

        sPattern = r'(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>'
        aResult = oParser.parse(sHtmlContent, sPattern)
        if aResult[0]:
            try:
                from resources.lib.packer import cPacker
                sHtmlContent2 = cPacker().unpack(aResult[1][0])
                sPattern2 = r'(?:file|src|source)\s*[:=]\s*["\']?(https?://[^"\'<>\s]+)'
                aResult2 = oParser.parse(sHtmlContent2, sPattern2)
                if aResult2[0]:
                    api_call = aResult2[1][0]
                    if api_call.startswith('//'):
                        api_call = 'https:' + api_call
                    return True, api_call + '|Referer=' + self._url
            except Exception:
                pass

        return False, False
