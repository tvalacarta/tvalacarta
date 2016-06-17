# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Clan TV
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re

from core import logger
from core import scrapertools
from core.item import Item
from core import jsontools

DEBUG = True
__channel__ = "clantve"
MAIN_URL = "http://www.rtve.es/api/agr-programas/490/programas.json?size=60&page=1"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.clantv mainlist")

    itemlist = []
    #itemlist.append( Item(channel=__channel__, title="Últimos vídeos añadidos" , url="http://www.rtve.es/infantil/components/TE_INFDEF/videos/videos-1.inc" , action="ultimos_videos" , folder=True) )
    itemlist.append( Item(channel=__channel__, title="Todos los programas" , url=MAIN_URL , action="programas" , folder=True, view="programs") )
    return itemlist

def programas(item, load_all_pages=False):
    logger.info("tvalacarta.channels.clantv programas")

    itemlist = []

    if item.url=="":
        item.url = MAIN_URL

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info("data="+data)
    json_object = jsontools.load_json(data)
    logger.info("json_object="+repr(json_object))
    json_items = json_object["page"]["items"]

    for json_item in json_items:
        title = json_item["name"]
        url = json_item["uri"]
        thumbnail = json_item["logo"]
        if json_item["description"] is not None:
            plot = json_item["description"]
        else:
            plot = ""
        fanart = json_item["imgPortada"]
        page = json_item["htmlUrl"]
        if (DEBUG): logger.info(" title=["+repr(title)+"], url=["+repr(url)+"], thumbnail=["+repr(thumbnail)+"] plot=["+repr(plot)+"]")
        itemlist.append( Item(channel=__channel__, title=title , action="episodios" , url=url, thumbnail=thumbnail, plot=plot , page=page, show=title , fanart=fanart, folder=True, view="videos") )

    # Añade el resto de páginas, siempre que haya al menos algún elemento
    if len(itemlist)>0:
        current_page = scrapertools.find_single_match(item.url,'page=(\d+)')
        next_page = str( int(current_page)+1 )
        next_page_url = item.url.replace("page="+current_page,"page="+next_page)

        if load_all_pages:
            item.url = next_page_url
            itemlist.extend(programas(item,load_all_pages))
        else:
            itemlist.append( Item(channel=__channel__, title=">> Página siguiente" , url=next_page_url,  action="programas", view="programs") )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.clantv episodios")

    itemlist = []

    # Descarga la página
    url = item.url+"/videos.json"
    data = scrapertools.cache_page(url)
    json_object = jsontools.load_json(data)
    #logger.info("json_object="+json_object)
    json_items = json_object["page"]["items"]

    for json_item in json_items:
        title = json_item["longTitle"]
        url = json_item["uri"]
        thumbnail = json_item["imageSEO"]
        if json_item["description"] is not None:
            plot = scrapertools.htmlclean(json_item["description"])
        else:
            plot = ""
        fanart = item.fanart
        page = json_item["htmlUrl"]
        aired_date = scrapertools.parse_date(json_item["publicationDate"])

        ms = json_item["duration"]
        if ms is None:
            duration=""
        else:
            x = ms / 1000
            seconds = x % 60
            x /= 60
            minutes = x % 60
            x /= 60
            hours = x % 24
            if hours>0:
                duration = str(hours)+":"+str(minutes)+":"+str(seconds)
            else:
                duration = str(minutes)+":"+str(seconds)

        if (DEBUG): logger.info(" title=["+repr(title)+"], url=["+repr(url)+"], thumbnail=["+repr(thumbnail)+"] plot=["+repr(plot)+"]")
        itemlist.append( Item(channel="rtve", title=title , action="play" , server="rtve", page=page, url=url, thumbnail=thumbnail, fanart=thumbnail, show=item.show , plot=plot , duration=duration, aired_date=aired_date, viewmode="movie_with_plot", folder=False) )

    from core import config
    if config.is_xbmc() and len(itemlist)>0:
        itemlist.append( Item(channel=item.channel, title=">> Opciones para esta serie", url=item.url, action="serie_options##episodios", thumbnail=item.thumbnail, show=item.show, folder=False))

    return itemlist

def play(item):

    item.server="rtve";
    itemlist = [item]

    return itemlist

def detalle_episodio(item):

    item.geolocked = "1"

    try:
        from servers import rtve as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

# Test de canal
# Devuelve: Funciona (True/False) y Motivo en caso de que no funcione (String)
def test():
    
    # Carga el menu principal
    items_mainlist = mainlist(Item())

    # Busca el item con la lista de programas
    items_programas = []
    for item_mainlist in items_mainlist:

        if item_mainlist.action=="programas":
            items_programas = programas(item_mainlist)
            break

    if len(items_programas)==0:
        return False,"No hay programas"

    # Carga los episodios
    items_episodios = episodios(items_programas[0])
    if len(items_episodios)==0:
        return False,"No hay episodios en "+items_programas[0].title

    # Lee la URL del vídeo
    #item_episodio = detalle_episodio(items_episodios[0])
    #if item_episodio.media_url=="":
    #    return False,"El conector no devuelve enlace para el vídeo "+item_episodio.title

    return True,""
