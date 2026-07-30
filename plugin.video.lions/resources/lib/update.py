# -*- coding: utf-8 -*-
# https://github.com/Kodi-vStream/venom-xbmc-addons


from resources.lib.comaddon import addon, siteManager, VSlog
from resources.lib.handler.requestHandler import cRequestHandler
import datetime, time, xbmc, re

class cUpdate:

    REPO_URL = 'https://rhoulou.github.io/atlas/repo'
    ADDON_ID = 'plugin.video.lions'

    def getUpdateSetting(self):
        addons = addon()

        self.checkAddonVersion()

        setting_time = addons.getSetting('setting_time')
        if not setting_time:
            setting_time = '2000-09-23 10:59:50.877000'

        time_now = datetime.datetime.now()
        time_service = self.__strptime(setting_time)
        pluginsupdateduration = int(addons.getSetting('pluginsupdateduration'))
        time_sleep = datetime.timedelta(hours = pluginsupdateduration)
        if time_now - time_service > time_sleep:

            sUrl = self.REPO_URL + '/sites.json'
            oRequestHandler = cRequestHandler(sUrl)
            properties = oRequestHandler.request(jsonDecode=True)
            if properties == "":
                return
            siteManager().setDefaultProps(properties)

            addons.setSetting('setting_time', str(time_now))

    def checkAddonVersion(self):
        addons = addon()
        sInstalled = addons.getAddonInfo('version')

        sUrl = self.REPO_URL + '/addons.xml'
        oRequestHandler = cRequestHandler(sUrl)
        sXml = oRequestHandler.request()
        if not sXml:
            return

        aMatch = re.search(r'<addon id="' + self.ADDON_ID + r'"[^>]*version="([^"]+)"', sXml)
        if not aMatch:
            return

        sRepo = aMatch.group(1)

        if self._isNewer(sRepo, sInstalled):
            VSlog(f'[{self.ADDON_ID}] Update found: {sInstalled} -> {sRepo}')
            xbmc.executebuiltin('UpdateAddon(' + self.ADDON_ID + ')')

    def _isNewer(self, v1, v2):
        a1 = v1.split('.')
        a2 = v2.split('.')
        for i in range(max(len(a1), len(a2))):
            n1 = int(a1[i]) if i < len(a1) else 0
            n2 = int(a2[i]) if i < len(a2) else 0
            if n1 > n2:
                return True
            elif n1 < n2:
                return False
        return False


    # formattage date (bug python)
    def __strptime(self, date):
        if len(date) > 19:
            format = '%Y-%m-%d %H:%M:%S.%f'
        else:
            format = '%Y-%m-%d %H:%M:%S'
        try:
            date = datetime.datetime.strptime(date, format)
        except TypeError:
            date = datetime.datetime(*(time.strptime(date, format)[0:6]))
        return date
