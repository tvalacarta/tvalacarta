# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal EARTH TV en YouTube
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

from core import logger
from core import scrapertools
from core.item import Item
from servers import youtube

logger.info("[clantv.py] init")

DEBUG = True
CHANNELNAME = "earthtv"
MODO_CACHE=0

def isGeneric():
    return True

def mainlist(item):
    logger.info("[earthtv.py] mainlist")

    itemlist = []

    # Añade al listado de XBMC
    itemlist.append( Item(channel=CHANNELNAME, title="Novedades" , action="novedades" , folder=True) )

    # Playlists
    itemlist.extend(youtube.getplaylists("earthTV",1,13,CHANNELNAME,"playlist"))

    return itemlist

def novedades(item):
    logger.info("[earthtv.py] novedades")
    itemlist = youtube.getuploads("earthTV",1,10,CHANNELNAME,"play")

    return itemlist

def playlist(item):
    logger.info("[earthtv.py] playlist")
    itemlist = youtube.getplaylistvideos(item.url,1,10,CHANNELNAME,"play")
    return itemlist

def play(item):
    logger.info("[earthtv.py] play")

    itemlist = []

    # Extrae el ID
    id = youtube.Extract_id(item.url)
    logger.info("[earthtv.py] id="+id)
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    
    # Obtiene la URL
    url = youtube.geturls(id,data)

    itemlist.append( Item(channel=CHANNELNAME, title=item.title , action="play" , server="Directo", url=url, thumbnail=item.thumbnail , folder=False) )

    return itemlist