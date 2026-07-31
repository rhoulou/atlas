# -*- coding: utf-8 -*-
import re
import urllib.parse

from resources.hosters.hoster import iHoster
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.comaddon import VSlog
from resources.lib import random_ua

UA = random_ua.get_phone_ua()

SNRT_TOKEN_URL = 'https://vod.forja.ma/snrt?url='


class cHoster(iHoster):

    def __init__(self):
        iHoster.__init__(self, 'forja_ma', 'Forja')

    def _getMediaLinkForGuest(self, autoPlay=False):
        sMediaUrl = self._url

        oRequest = cRequestHandler(sMediaUrl)
        oRequest.addHeaderEntry('user-agent', UA)
        sMediaUrl = oRequest.request()
        sMediaUrl = sMediaUrl.strip()

        sMediaUrl = sMediaUrl.replace('//vod/', '/vod/')

        oTokenRequest = cRequestHandler(SNRT_TOKEN_URL + urllib.parse.quote(sMediaUrl, safe=''))
        oTokenRequest.addHeaderEntry('user-agent', UA)
        sTokenData = oTokenRequest.request()

        oMatch = re.search(r'verify=([^&\s]+)&expires=([^&\s]+)', sTokenData)
        if not oMatch:
            VSlog('forja: token lookup failed (' + sTokenData[:200] + ')')
            return False, False

        sSeparator = '&' if '?' in sMediaUrl else '?'
        sMediaUrl = sMediaUrl + sSeparator + 'verify=' + oMatch.group(1) + '&expires=' + oMatch.group(2)

        if sMediaUrl:
            return True, sMediaUrl
        return False, False
