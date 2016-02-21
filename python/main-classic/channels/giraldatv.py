# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Giralda TV
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import youtube_channel

DEBUG = True

def isGeneric():
    return True

def mainlist(item):
    return youtube_channel.playlists(item,"giraldatv")

def test():
    return youtube_channel.test("giraldatv")
