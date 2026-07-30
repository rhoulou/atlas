from resources.hosters.hoster import iHoster

class cHoster(iHoster):

    def __init__(self):
        iHoster.__init__(self, 'elementum', 'Elementum')

    def _getMediaLinkForGuest(self):
        return True, self._url
