# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para UPV TV
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib,re

from core import logger
from core import scrapertools
from core.item import Item 

logger.info("tvalacarta.channels.upvtv init")

DEBUG = False
CHANNELNAME = "upvtv"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.upvtv mainlist")

    item.url="http://www.upv.es/rtv/tv/carta"
    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.upvtv programas")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    patron = '<ul data-categoria(.*?)</ul>'
    bloques = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(bloques)

    for bloque in bloques:

        patron  = '<li(.*?)</li'
        matches = re.compile(patron,re.DOTALL).findall(bloque)
        if DEBUG: scrapertools.printMatches(matches)

        for match in matches:
            title = scrapertools.find_single_match(match,'title="([^"]+)"')
            if title=="":
                title = scrapertools.find_single_match(match,'<a[^>]+>([^<]+)</a>')
            title = title.decode('iso-8859-1').encode("utf8","ignore")
            thumbnail = scrapertools.find_single_match(match,'<img.*?src="([^"]+)"')
            plot = scrapertools.find_single_match(match,'<span class="tex_imagen"[^<]+<br />([^<]+)</span>')
            url = scrapertools.find_single_match(match,'a href="([^"]+)"')
            url = urlparse.urljoin(item.url,url)
            if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
            itemlist.append( Item( channel=CHANNELNAME , title=title , action="episodios" , url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=True ) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.upvtv episodios")
    itemlist=[]

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.find_single_match(data,'<h1>Programas anteriores(.*?)</ul')

    # Extrae los capitulos
    patron  = '<li[^<]+'
    patron += '<span class="enlace"><a href="([^"]+)" >([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.replace("\n"," ")
        title = re.compile("\s+",re.DOTALL).sub(" ",title)
        title = title.decode('iso-8859-1').encode("utf8","ignore")
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=CHANNELNAME , title=title , action="play" , server="upvtv" , url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=False ) )

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    # Todas las opciones tienen que tener algo
    programas_items = mainlist(Item())
    if len(programas_items)==0:
        return False

    episodios_items = episodios(programas_items[0])
    if len(episodios_items)==0:
        return False

    return bien
