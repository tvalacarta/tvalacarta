# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Once 11 (mx)
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

DEBUG = True
CHANNELNAME = "oncetvmex"

def isGeneric():
    return True

# Entry point
def mainlist(item):
    return youtube_channel.playlists(item,"CanalOnceIPN")

def test():
    return youtube_channel.test("CanalOnceIPN")