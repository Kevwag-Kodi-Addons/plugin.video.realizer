# -*- coding: utf-8 -*-

'''
realizer MAIN MODULE SCRAPER
'''

import sys,pkgutil,re,json,urllib,random,datetime,time,os,xbmc

try:
    import urlparse
except:
    from urllib.parse import urlparse

from resources.lib.modules import control
from resources.lib.modules.log_utils import debug
from resources.lib.api import debrid

control.moderator()

class sources:
    
    def __init__(self):
        self.sources = []
        self.matchTitle = control.setting('scraper.matchtitle')
        
    def play(self, title, year, imdb, tvdb, season, episode, tvshowtitle, premiered, meta, clearlogo, plot):
            url = None
            debug('PLAY ITEM:', title)
            
            title = tvshowtitle if not tvshowtitle == None else title
            
            if tvshowtitle == None: 
                season = None
                episode = None
                    
            url, id = debrid.scrapecloud(title, year=year, season=season, episode=episode)
            #xbmc.log(str(url)+'url===>PHIL', level=xbmc.LOGINFO)
            #xbmc.log(str(id)+'id===>PHIL', level=xbmc.LOGINFO)

            if url == None or url =='' or url == '0':
                return self.errorForSources()

            try: meta = json.loads(meta)
            except: pass
            #xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
            from resources.lib.modules.player import player
            player().run(title, year, season, episode, imdb, tvdb, url, meta, id, clearlogo)

    def directPlay(self, url, title, year, imdb, tvdb, season, episode, tvshowtitle, premiered, meta, id, name, clearlogo):
        try:
            debug('PLAY ITEM:', title, id)
            
            title = tvshowtitle if not tvshowtitle == None else title
                        
            if url == None or url =='' or url == '0':
                return self.errorForSources()
            
            elif url == 'resolve':

                torrFile = debrid.torrentItemToDownload(name, id)
                control.infoDialog('Playing Torrent Item', torrFile['filename'], time=3)
                url = torrFile['download']
                id  = torrFile['id']
                if url == None: return self.errorForSources()
                
            try: meta = json.loads(meta)
            except: pass

            from resources.lib.modules.player import player
            player().run(title, year, season, episode, imdb, tvdb, url, meta, id, clearlogo)
        except:
            pass
            
            


            
    def errorForSources(self):
        control.infoDialog(control.lang(32401).encode('utf-8'), sound=False)
