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
LIVE_URL = "http://aztecalive-lh.akamaihd.net/i/0e3hprpxt_1@735658/master.m3u8"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.adn40 mainlist")

    return categorias(item)

def categorias(item):
    logger.info("tvalacarta.channels.adn40 categorias")

    item.url = "http://www.adn40.mx/json/videoteca/index.json"

    itemlist = []

    itemlist.append( Item(channel=CHANNELNAME, title="Ver señal en directo" , action="play", server="directo", url=LIVE_URL, category="programas", folder=False) )

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

def directos(item=None):
    logger.info("tvalacarta.channels.adn40 directos")

    itemlist = []

    itemlist.append( Item(channel=CHANNELNAME, title="ADN 40",   url=LIVE_URL, thumbnail="http://media.tvalacarta.info/canales/128x128/adn40.png", category="Nacionales", action="play", folder=False ) )

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
    categorias_itemlist = mainlist(Item())
    if len(categorias_itemlist)<=1:
        return False,"No hay categorias en el menu principal"

    categoria_item = categorias_itemlist[1]
    programas_itemlist = programas(categoria_item)
    if len(programas_itemlist)==0:
        return False,"No hay programas en la categoria "+categoria_item.title

    programa_item = programas_itemlist[0]
    episodios_itemlist = episodios(programa_item)

    if len(episodios_itemlist)==0:
        return False,"No hay episodios en "+programa_item.title

    episodio_item = episodios_itemlist[0]

    from servers import adn40 as server
    video_urls = server.get_video_url(episodio_item.url)

    if len(video_urls)==0:
        return False,"No funciona el vídeo "+episodio_item.title+" en el programa "+programa_item.title

    # Verifica los directos
    directos_itemlist = directos(Item())

    for directo_item in directos_itemlist:

        try:
            data = scrapertools.cache_page(directo_item.url)
        except:
            return False,"Falla el canal en directo "+directo_item.title

    return True,""
