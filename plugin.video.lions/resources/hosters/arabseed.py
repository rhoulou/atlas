#-*- coding: utf-8 -*-

from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import dialog
from resources.hosters.hoster import iHoster
from resources.lib.comaddon import VSlog

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36'

class cHoster(iHoster):

    def __init__(self):
        iHoster.__init__(self, 'arabseed', 'arabseed')

    def isDownloadable(self):
        return True

    def setUrl(self, sUrl):
        self._url = str(sUrl)

    def _getMediaLinkForGuest(self):
        VSlog(self._url)
        sUrl = self._url

        oRequest = cRequestHandler(self._url)
        oRequest.addHeaderEntry('Referer', 'https://arabseed.rocks/')
        sHtmlContent = oRequest.request()
        oParser = cParser()

        api_call = False

        sPattern = '<video[^>]*src="([^"]+\.mp4[^"]*)"'
        aResult = oParser.parse(sHtmlContent, sPattern)
        if aResult[0]:
            api_call = aResult[1][0]

        if not api_call:
            sPattern = '<source src="([^"]+)"[^>]*type="video/mp4"'
            aResult = oParser.parse(sHtmlContent, sPattern)
            if aResult[0]:
                api_call = aResult[1][0]

        if not api_call:
            sPattern = 'src=["\']([^"\']+\.mp4[^"\']*)["\']'
            aResult = oParser.parse(sHtmlContent, sPattern)
            if aResult[0]:
                api_call = aResult[1][0]

        if api_call:
            if api_call.startswith('//'):
                api_call = 'https:' + api_call
            return True, api_call + '|User-Agent=' + UA + '&verifypeer=false'

        return False, False
