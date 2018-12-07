# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Canal 22 (México)
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import config
from core import logger
from core import scrapertools
from core import jsontools
from core.item import Item
import youtube_channel

CHANNELNAME="canal22"

def isGeneric():
    return True

def mainlist(item):

    itemlist = []
    
    # El primer nivel de menú es un listado por canales
    itemlist.append( Item(channel=CHANNELNAME, title="Directos"          , action="loadlives", folder=True))

    itemlist.extend(youtube_channel.playlists(item,"canal22"))

    return itemlist

def test():
    return youtube_channel.test("canal22")

def loadlives(item):
    logger.info("tvalacarta.channels.rtve play loadlives")

    itemlist = []

    for directo in directos(item):
        itemlist.append(directo)

    return itemlist

def directos(item=None):
    logger.info("tvalacarta.channels.rtve directos")

    itemlist = []

    itemlist.append( Item(channel=CHANNELNAME, title="Canal 22",        url="http://api.new.livestream.com/accounts/27390802/events/8239465/live.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/canal22.png", category="Nacionales", action="play", folder=False ) )

    return itemlist
