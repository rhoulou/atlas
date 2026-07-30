#coding: utf-8
import re
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.hosters.hoster import iHoster
from resources.lib.packer import cPacker
from resources.lib.comaddon import VSlog


class cHoster(iHoster):

    def __init__(self):
        iHoster.__init__(self, 'peytonepre', 'PeytonEpre')

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

        sPattern = r'(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>'
        aResult = oParser.parse(sHtmlContent, sPattern)

        if aResult[0]:
            for aEntry in aResult[1]:
                try:
                    sHtmlContent2 = cPacker().unpack(aEntry)

                    sPattern2 = r'(?:file|source|src|url)\s*[:=]\s*["\']?(https?://[^"\'<>\s]+)'
                    aResult2 = oParser.parse(sHtmlContent2, sPattern2)
                    if aResult2[0]:
                        api_call = aResult2[1][0]
                        if api_call.startswith('//'):
                            api_call = 'https:' + api_call
                        return True, api_call + '|Referer=' + self._url

                    sPattern3 = r'["\']?(https?://[^"\'<>\s]+\.m3u8[^"\'<>\s]*)'
                    aResult3 = oParser.parse(sHtmlContent2, sPattern3)
                    if aResult3[0]:
                        api_call = aResult3[1][0]
                        if api_call.startswith('//'):
                            api_call = 'https:' + api_call
                        return True, api_call + '|Referer=' + self._url
                except Exception:
                    continue

        return False, False
