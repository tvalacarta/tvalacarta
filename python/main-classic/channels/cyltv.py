# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para cyltv (youtube)
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import scrapertools
from core.item import Item
import youtube_channel

DEBUG = False
CHANNELNAME = "cyltv"
YOUTUBE_CHANNEL_ID = "cyltelevision"

def isGeneric():
    return True

# Entry point
def mainlist(item):
    return youtube_channel.playlists(item,YOUTUBE_CHANNEL_ID)

def test():
    return youtube_channel.test(YOUTUBE_CHANNEL_ID)
