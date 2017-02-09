# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para TVR (La Rioja)
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import logger
from core import config
from core import scrapertools
from core.item import Item

DEBUG = True
CHANNELNAME = "tvr"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.tvr mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Informativos"  , action="programas" , url="http://www.tvr.es/programas/informativos-tvr/", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Programas"  , action="programas" , url="http://www.tvr.es/programas-2/", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Deportes" , action="programas" , url="http://www.tvr.es/deportes/", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Producciones TVR"    , action="programas" , url="http://www.tvr.es/especiales/", folder=True) )

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.tvr programas")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data,'<div id="post[^<]+<div class="entry">(.*?)</div')

    patron  = '<a href="([^"]+)"[^<]+'
    patron += '<img.*?src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail in matches:
        title = scrapedurl.strip()
        if title.endswith("/"):
            title = title[:-1]
        title = title.split("/")[-1]
        title = title.replace("-"," ")
        title = title.capitalize()
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="episodios" , url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=True ) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.tvr episodios")
    
    '''
    <div id="playlist">
    <a href="http://www.tvr.es/videos/degusta/DEGUSTA LA RIOJA 12-01-17 1 BLOQUE.mp4" class="titulo">DEGUSTA LA RIOJA 12-01-17 1 BLOQUE</a>
    <a href="http://www.tvr.es/videos/degusta/DEGUSTA LA RIOJA 12-01-17 2 BLOQUE.mp4" class="titulo">DEGUSTA LA RIOJA 12-01-17 2 BLOQUE</a><a href="http://www.tvr.es/videos/degusta/DEGUSTA LA RIOJA 12-01-17 3 BLOQUE.mp4" class="titulo">DEGUSTA LA RIOJA 12-01-17 3 BLOQUE</a></div>
    '''

    itemlist = []
    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data,'<div id="playlist">(.*?)</div')

    patron  = '<a href="([^"]+)[^>]+>([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.strip()
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="play" , url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=False ) )

    return itemlist

def play(item):
    return [item]

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    
    # El canal tiene estructura
    items_mainlist = mainlist(Item())
    items_programas = []

    # Todas las opciones del menu tienen que tener algo
    for item_mainlist in items_mainlist:
        exec "itemlist="+item_mainlist.action+"(item_mainlist)"
    
        if len(itemlist)==0:
            print "La sección '"+item_mainlist.title+"' no devuelve nada"
            return False

        items_programas = itemlist

    # Ahora recorre los programas hasta encontrar vídeos en alguno
    for item_programa in items_programas:
        print "Verificando "+item_programa.title
        items_episodios = episodios(item_programa)

        if len(items_episodios)>0:
            return True

    print "No hay videos en ningún programa"
    return False
