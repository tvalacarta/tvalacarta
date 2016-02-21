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

__channel__ = "cadenatres"
__category__ = "F"
__type__ = "generic"
__title__ = "cadenatres"
__language__ = "ES"
__creationdate__ = "20130321"
__vfanart__ = "http://www.cadenatres.com.mx/sites/www.cadenatres.com.mx/themes/cadena2/images/back.jpg"

DEBUG = config.get_setting("debug")

def isGeneric():

    return True
def mainlist(item):
    logger.info("[cadenatres.py] mainlist")
    itemlist=[]

    itemlist.append( Item(channel=__channel__, title="Noticias" , action="playlists" , url="Cadena3Noticias", folder=True) )
    itemlist.append( Item(channel=__channel__, title="Deportes" , action="playlists" , url="Cadena3Deportes", folder=True) )
    itemlist.append( Item(channel=__channel__, title="Espectaculos" , action="playlists" , url="Cadena3Espectaculos", folder=True) )
    itemlist.append( Item(channel=__channel__, title="Series" , action="playlists" , url="Cadena3Series", folder=True) )
    itemlist.append( Item(channel=__channel__, title="Vida y Hogar" , action="playlists" , url="Cadena3VidayHogar", folder=True) )

    return itemlist

def playlists(item):
    return youtube_channel.playlists(item,item.url)

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    # Cada elemento de mainlist es un canal de Cadena 3
    mainlist_items = mainlist(Item())

    for mainlist_item in mainlist_items:

        # Si hay algún video en alguna de las listas de reproducción lo da por bueno
        playlist_items = playlists(mainlist_item)
        for playlist_item in playlist_items:
            items_videos = videos(playlist_item)
            if len(items_videos)>0:
                return True

    return False