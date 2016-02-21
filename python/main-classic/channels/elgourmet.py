# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# creado por rsantaella
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools
import youtube_channel

__channel__ = "elgourmet"
__category__ = "F"
__type__ = "generic"
__title__ = "elgourmet"
__language__ = "ES"
__creationdate__ = "20121216"
__vfanart__ = "http://elgourmet.com/imagenes/background.jpg"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    return youtube_channel.playlists(item,"elgourmetcomLatam")

def test():
    return youtube_channel.test("elgourmetcomLatam")
