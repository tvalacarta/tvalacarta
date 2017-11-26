# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para ecuador tv
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import os
import sys

import urlparse,re
import urllib
import datetime

from core import logger
from core import scrapertools
from core.item import Item

import youtube_channel

__channel__ = "ecuadortv"

DEBUG = True
YOUTUBE_CHANNEL_ID = "RTVEcuador"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.ecuadortv mainlist")
    return youtube_channel.playlists(item,YOUTUBE_CHANNEL_ID)
