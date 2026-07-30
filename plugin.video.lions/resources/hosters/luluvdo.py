#coding: utf-8
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.hosters.hoster import iHoster

class cHoster(iHoster):

    def __init__(self):
        iHoster.__init__(self, 'luluvdo', 'Lulu')

    def isDownloadable(self):
        return False

    def setUrl(self, url):
        self._url = str(url)

    def _getMediaLinkForGuest(self):
        api_call = ''

        oRequest = cRequestHandler(self._url)
        oRequest.addHeaderEntry('Referer', 'https://aflamfree.one/')
        sHtmlContent = oRequest.request()

        oParser = cParser()

        sPattern = r'source\s*:\s*["\']([^"\']+\.mp4[^"\']*)["\']'
        aResult = oParser.parse(sHtmlContent, sPattern)
        if aResult[0]:
            api_call = aResult[1][0]

        if not api_call:
            sPattern = r'file\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']'
            aResult = oParser.parse(sHtmlContent, sPattern)
            if aResult[0]:
                api_call = aResult[1][0]

        if not api_call:
            sPattern = r'(https?://[^"\']+\.m3u8[^"\']*)'
            aResult = oParser.parse(sHtmlContent, sPattern)
            if aResult[0]:
                api_call = aResult[1][0]

        if not api_call:
            sPattern = r'(https?://[^"\']+\.mp4[^"\']*)'
            aResult = oParser.parse(sHtmlContent, sPattern)
            if aResult[0]:
                api_call = aResult[1][0]

        if api_call:
            if api_call.startswith('//'):
                api_call = 'https:' + api_call
            return True, api_call

        return False, False
