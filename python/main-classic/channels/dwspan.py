# -*- coding: utf-8 -*-
#------------------------------------------------------------------
# tvalacarta
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------------
# Canal para "Deustche Welle en español", creado por rsantaella
#------------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools
from core import jsontools

__channel__ = "dwspan"
__category__ = "F"
__type__ = "generic"
__title__ = "dwspan"
__language__ = "ES"
__creationdate__ = "20121130"
__vfanart__ = "http://www.dw.de/cssi/dwlogo-print.gif"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.dwspan mainlist")
    return programas(Item())

def programas(item):
    logger.info("tvalacarta.channels.dwspan programas")    
    
    # Descarga la página
    data = scrapertools.cache_page("http://mediacenter.dw.de/ajax/spanish/programm/interval/all/")
    logger.info(data)

    programas_json = jsontools.load_json(data)
    if programas_json == None:
        return []

    itemlist = []
    for programa in programas_json:
        logger.info(repr(programa))
        title = programa['_name']
        url = 'http://mediacenter.dw.de/ajax/spanish/mediaselect/video/?programm='+str(programa['_id'])
        itemlist.append( Item(channel=__channel__, title=title , action="episodios" , url=url, show=title, folder=True) )

    return itemlist

def detalle_programa(item):
    logger.info("tvalacarta.channels.dwspan detalle_programa")    

    id_programa = scrapertools.find_single_match(item.url,"programm=(\d+)")
    url = "http://www.dw.com/es/programa/a/s-"+id_programa+"-1"

    try:
        item.page = scrapertools.get_header_from_response(url,header_to_get="location")
        data = scrapertools.cache_page(item.page)

        item.plot = scrapertools.find_single_match(data,'<div class="longText">(.*?)</div>')
        item.plot = scrapertools.htmlclean( item.plot ).strip()
        if item.plot=="":
            item.plot = scrapertools.find_single_match(data,'<div class="news"[^<]+<h2[^<]+</h2>(.*?)</div>')
            item.plot = scrapertools.htmlclean( item.plot ).strip()

        item.thumbnail = scrapertools.find_single_match(data,'<input type="hidden" name="preview_image" value="([^"]+)"')
        if item.thumbnail.strip()=="":
            item.thumbnail = scrapertools.find_single_match(data,'<img class="stillImage" src="([^"]+)"')
        item.thumbnail = urlparse.urljoin(item.page,item.thumbnail)
    except:
        import traceback
        logger.info(traceback.format_exc())

    return item

def episodios(item):
    logger.info("tvalacarta.channels.dwspan episodios")

    id_programa = scrapertools.find_single_match(item.url,"programm=(\d+)")
    data = scrapertools.cache_page(item.url)
    
    import json
    episodios_json = json.loads(data)
    if episodios_json == None : episodios_json = []
    
    itemlist = []
    last_episodio = ''
    for ep in episodios_json['mediaselect']:
        last_episodio = ep

        episodio = episodios_json['items'][ep]
        #logger.info("episodio="+repr(episodio))

        if episodio["getCSSClass"]=="audio":
            continue

        if episodio["parent_id"] is not None:
            continue

        title = episodio['title'].encode("utf8","ignore") + ' ' + episodio['getPublicationDate'].encode("utf8","ignore")
        thumbnail = episodio['getImages']['medium']['src'].replace("\\", "")
        plot = episodio['getDescription'].encode("utf8","ignore")

        aired_date = episodio['getPublicationDate'] or ""
        duration = episodio['getMetaInformation'] or ""
        duration = duration.replace("min.","").strip()
        url = episodio["ref_url"] or ""
        url = url.encode("utf8","ignore")

        media_url = episodio["getDirectAvLink"] or ""
        media_url = media_url.encode("utf8","ignore")

        if media_url == "":
            playpath = "mp4:%s_sor.mp4" % episodio["getFlvFile"].replace("\\", "")
            media_url= "rtmp://tv-od.dw.de/flash/ playpath=%s" % playpath
            media_url = media_url.encode("utf8","ignore")

        logger.info("tvalacarta.channels.dwspan episodios title="+title+", media_url="+media_url)

        itemlist.append( Item(channel=__channel__, action="play", title=title , url=url, media_url=media_url, plot=plot, thumbnail=thumbnail, aired_date=aired_date, duration=duration, show=item.show, folder=False) )

    if len(itemlist)>0:
        next_page_url = 'http://mediacenter.dw.de/ajax/spanish/mediaselect/video/item/%s/after/true/nochildren/true/?programm=%s' % (last_episodio, id_programa)
        itemlist.append( Item(channel=__channel__, action="episodios", title=">> Página siguiente" , url=next_page_url, show=item.show, folder=True) ) 
    
    return itemlist

def play(item,page_data=""):
    logger.info("tvalacarta.channels.dwspan play")

    item.server = "directo"
    item.url = item.media_url
    logger.info("tvalacarta.channels.dwspan play item.url="+item.url)
    itemlist = [item]

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    items_programas = mainlist(Item())
    for item_programa in items_programas:
        items_episodios = episodios(item_programa)

        if len(items_episodios)>0:
            return True

    return False
