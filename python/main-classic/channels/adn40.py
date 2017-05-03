# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para ADN 40 (México)
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import scrapertools
from core import jsontools
from core.item import Item

DEBUG = False
CHANNELNAME = "adn40"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.adn40 mainlist")

    return categorias(item)

def categorias(item):
    logger.info("tvalacarta.channels.adn40 categorias")

    item.url = "http://www.adn40.mx/json/videoteca/index.json"

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    json_data = jsontools.load_json(data)    

    for json_item in json_data["section"]:
        title = json_item["title"]
        url = urlparse.urljoin(item.url,json_item["link"])
        thumbnail = ""
        plot = ""

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="programas", folder=True) )

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.adn40 programas")

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    json_data = jsontools.load_json(data)    

    for json_item in json_data["program"]:
        title = json_item["title"]

        #/videoteca/cultura/el-foco
        #http://www.adn40.mx/json/videoteca/programs/el-foco.json
        show_id = scrapertools.find_single_match(json_item["link"],"/([^/]+)$")
        url = "http://www.adn40.mx/json/videoteca/programs/"+show_id+".json"
        thumbnail = ""
        plot = ""

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="episodios", show=title, folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.adn40 episodios")

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    json_data = jsontools.load_json(data)    

    for json_item in json_data["video"]:
        title = json_item["title"]
        url = json_item["link"]
        thumbnail = json_item["image"]
        plot = json_item["teaser"]
        aired_date = scrapertools.parse_date(json_item["date"])

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="play", server="adn40", show=item.show, folder=False) )

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    # Comprueba que la primera opción tenga algo
    categorias_items = mainlist(Item())
    programas_items = programas(categorias_items[0])
    episodios_items = episodios(programas_items[0])

    if len(episodios_items)>0:
        return True

    return False