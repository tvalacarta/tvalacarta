# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para RTVCE (Ceuta)
# creado por rsantaella
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "rtvceuta"
__title__ = "rtvceuta"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.rtvceuta mainlist")

    item.url="http://www.rtvce.es/programas"
    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.rtvceuta programas")    

    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    patron  = '<div class="boxProg[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img class="mar[^"]+" src="([^"]+)" width="[^"]+" height="[^"]+" alt="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapedtitle
        title = scrapedtitle.lower()
        title = scrapertools.htmlclean(title)
        title = unicode(title,"utf-8").capitalize().encode("utf-8")
        plot = ""

        itemlist.append( Item(channel=__channel__, action="episodios", title=title, show=title, url=url, thumbnail=thumbnail,  plot=plot, folder=True))

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.url)
    item.thumbnail = scrapertools.find_single_match(data,'<meta content="([^"]+)" itemprop="thumbnailUrl')

    item.plot = scrapertools.find_single_match(data,'<div class="item-text"><p class="introtext">(.*?)</div>')
    item.plot = scrapertools.htmlclean(item.plot).strip()

    return item

def episodios(item):
    logger.info("tvalacarta.channels.rtvceuta episodios")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)    
    url = scrapertools.find_single_match(data,'<div class="descargas"(.*?)</ul>')

    patron  = '<li[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img[^>]+>([^<]+)</a>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle
        thumbnail = ""

        # Codifica el vídeo como un parametro de la página del programa, para poder obtenerlo después y seguir teniendo un enlace válido al episodio

        # programa: http://www.rtvce.es/programas/28-on-line
        # video: http://teledifusionvod.es:7088/html5ceutatv/ftpceutatv/online/febrero/ONLINE%2011-02-2016.mp4
        # resultado: http://www.rtvce.es/programas/28-on-line?url=http%3A%2F%2Fteledifusionvod.es%3A7088%2Fhtml5ceutatv%2Fftpceutatv%2Fonline%2Ffebrero%2FONLINE%252011-02-2016.mp4

        video_url = urllib.urlencode({"url":scrapedurl})
        url = item.url + "?" + video_url

        plot = ""
        itemlist.append( Item(channel=__channel__, action="play", title=title, url=url, thumbnail=thumbnail, plot=plot, show=item.show, folder=False))

    next_page_url = scrapertools.find_single_match(data,'<a class="nextpostslink" rel="next" href="([^"]+)">')
    if next_page_url!="":
        itemlist.append( Item(channel=__channel__, title=">> Página siguiente" , action="episodios" , url=urlparse.urljoin(item.url,next_page_url), show=item.show) )

    return itemlist

def play(item):
    logger.info("tvalacarta.channels.rtvceuta play")

    # Extrae el parámetro "url" recibido, ese es el vídeo
    import urlparse
    parsed_url = urlparse.urlparse(item.url)
    logger.info("tvalacarta.channels.rtvceuta parsed_url="+repr(parsed_url))
    params = urlparse.parse_qs(parsed_url.query)
    logger.info("tvalacarta.channels.rtvceuta params="+repr(params))
    logger.info("tvalacarta.channels.rtvceuta url="+repr(params["url"][0]))

    itemlist = []
    itemlist.append( Item(channel=__channel__, action="play", title=item.title, url=params["url"][0], thumbnail=item.thumbnail, plot=item.plot, show=item.show, folder=False))

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    
    # Mainlist es la lista de programas
    programas_items = mainlist(Item())
    if len(programas_items)==0:
        print "No encuentra los programas"
        return False

    episodios_items = videos(programas_items[0])
    if len(episodios_items)==0:
        print "El programa '"+programas_items[0].title+"' no tiene episodios"
        return False

    return True
