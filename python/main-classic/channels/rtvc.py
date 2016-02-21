# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para RTVC
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
CHANNELNAME = "rtvc"

def isGeneric():
    return True

# Entry point
def mainlist(item):
    return youtube_channel.playlists(item,"TelevisionCanaria")

def test():
    return youtube_channel.test("TelevisionCanaria")