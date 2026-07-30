#-*- coding: utf-8 -*-
#Vstream https://github.com/Kodi-vStream/venom-xbmc-addons
from resources.hosters.hoster import iHoster
from resources.lib.comaddon import VSlog
import resolveurl

class cHoster(iHoster):

    def __init__(self):
        iHoster.__init__(self, 'resolver', 'ResolveURL')
        self.__sRealHost = ''
		
    def setRealHost(self, host):
        self.__sRealHost = "-" + host

    def setDisplayName(self, displayName):
        self._displayName = displayName + ' [COLOR violet]'+ self._defaultDisplayName + self.__sRealHost + '[/COLOR]'

    def _getMediaLinkForGuest(self):
        VSlog(self._url)
        try:
            sUrl = self._url.split('|')[0] if '|' in self._url else self._url
            hmf = resolveurl.HostedMediaFile(url=sUrl)
            if hmf.valid_url():
                stream_url = hmf.resolve()
                if stream_url:
                    if '|' not in stream_url:
                        stream_url = stream_url + '|verifypeer=false&Referer=' + self._url.split('|')[0].split('/e/')[0] + '/'
                    return True, stream_url
        except Exception as e:
            VSlog('Resolver error: %s' % str(e))

        return False, False


