# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Telefe
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse
import urllib
import re
import traceback

from core import logger
from core import scrapertools
from core import jsontools
from core.item import Item

DEBUG = True
CHANNELNAME = "telefe"
MAIN_URL = "http://telefe.com/capitulos-completos/"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.telefe mainlist")

    itemlist = []
    itemlist.extend(programas(item))

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.telefe programas")
    
    itemlist = []

    data = scrapertools.cache_page(MAIN_URL)
    data = scrapertools.find_single_match(data,'T3.content.cache = \{\s*"/capitulos-completos/"\:\s*(.*?)\}\;')

    json_data = jsontools.load_json(data)

    for json_item in json_data["children"]["bottom"]:
        logger.info("json_item="+repr(json_item))
        title = json_item["options"]["title"]
        url = urlparse.urljoin(MAIN_URL,json_item["options"]["deepLinks"][0]["url"])
        thumbnail = ""
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="videos" , url=url, thumbnail=thumbnail, plot=plot , show=title, folder=True) )

    return itemlist

def videos(item):
    logger.info("tvalacarta.channels.telefe videos")
    
    itemlist=[]
    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data,'T3.content.cache = \{\s*"[^"]+"\:\s*(.*?)\}\;')
    logger.info("tvalacarta.channels.telefe videos data="+data)

    json_data = jsontools.load_json(data)

    for json_item in json_data["children"]["bottom"]["children"]["a"]["collection"]:
        logger.info("json_item="+repr(json_item))
        title = json_item["title"]
        url = urlparse.urljoin(item.url,json_item["permalink"])
        thumbnail = urlparse.urljoin("http://static.cdn.telefe.com",json_item["images"][0]["url"])
        plot = json_item["description"]
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="play", server="telefe", url=url, thumbnail=thumbnail, plot=plot , show=title, folder=False) )

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    
    # El canal tiene estructura programas -> episodios -> play
    items_programas = programas(Item())
    if len(items_programas)==0:
        print "No hay programas"
        return False

    # Ahora recorre los programas hasta encontrar vídeos en alguno
    for item_programa in items_programas:
        print "Verificando "+item_programa.title
        items_videos = videos(item_programa)
        if len(items_videos)>0:
            return True

    print "No hay videos en ningún programa"
    return False
