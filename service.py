# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
import time

first_run_flag = False
realizer_helper_time = xbmcgui.Window(10000).getProperty("realizer_helper_time")
if str(realizer_helper_time) == '':
	xbmc.log(str('REALIZER_SLEEP')+'===>PHIL', level=xbmc.LOGINFO)
	time.sleep(5)

xbmcgui.Window(10000).setProperty("realizer_helper_time",'true')

#xbmc.log(str('REALIZER_SLEEP')+'===>PHIL', level=xbmc.LOGINFO)


from resources.lib.modules import control
control.setSetting(id='first.start', value='true') # FORCE NEW CACHE
control.execute('RunPlugin(plugin://plugin.video.realizer/?action=service)')	
class Service():
	def __init__(self, *args):
		addonName = 'Premiumize Transfers'

	def ServiceEntryPoint(self):
		import xbmc
		import xbmcgui
		monitor = xbmc.Monitor()
		updateTime = control.setting('rss.timeout')
		updateSeconds = int(updateTime) * 3600

		while not monitor.abortRequested():
			if monitor.waitForAbort(updateSeconds):
                # # Abort was requested while waiting. We should exit
				break
			
			if xbmcgui.Window(10000).getProperty('Next_EP.Realizer_Suppress') != 'True' and control.setting('rss.1') == 'true' or control.setting('rss.2') == 'true' or control.setting('rss.3') == 'true' or control.setting('rss.4') == 'true':	
				control.execute('RunPlugin(plugin://plugin.video.realizer/?action=rss_update)')
			if xbmcgui.Window(10000).getProperty('Next_EP.Realizer_Suppress') == 'True':
				control.setSetting(id='first.start', value='false')
				#xbmcgui.Window(10000).clearProperty('Next_EP.Realizer_Suppress')
				
Service().ServiceEntryPoint()			

