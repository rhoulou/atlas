#coding: utf-8
import base64
import re
from resources.hosters.hoster import iHoster
from resources.lib.comaddon import VSlog


class cHoster(iHoster):

    def __init__(self):
        iHoster.__init__(self, 'upbom', 'Upbom')

    def isDownloadable(self):
        return False

    def setUrl(self, url):
        self._url = str(url)

    def _getMediaLinkForGuest(self):
        VSlog(self._url)
        api_call = ''

        try:
            if '?' in self._url:
                qs = self._url.split('?', 1)[1]
                for param in qs.split('&'):
                    if '=' in param:
                        k, v = param.split('=', 1)
                        if k == 'url':
                            api_call = base64.b64decode(v + '==').decode('utf-8', errors='ignore')
                            break
        except Exception:
            pass

        if api_call:
            if api_call.startswith('//'):
                api_call = 'https:' + api_call
            return True, api_call + '|Referer=' + self._url.split('/d/')[0] + '/'

        return False, False
