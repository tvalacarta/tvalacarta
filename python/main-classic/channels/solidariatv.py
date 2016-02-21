# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta
# Canal para Solidaria TV
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import logger
from core import scrapertools
from core.item import Item

logger.info("[solidariatv.py] init")

DEBUG = False
CHANNELNAME = "solidariatv"

def isGeneric():
    return True

def mainlist(item):
    logger.info("[solidariatv.py] mainlist")

    # Descarga la página
    data = scrapertools.cachePage("http://www.solidariatv.com/")

    '''
    <tr align="left"><td><a href="http://www.solidariatv.com//index.php?option=com_content&amp;task=blogsection&amp;id=14&amp;Itemid=88" class="mainlevel" id="active_menu">SOLIDARIA TV</a></td></tr>

    '''

    # Extrae las entradas
    patron  = '<tr align="left"><td><a href="([^"]+)" class="mainlevel"[^>]+>([^<]+)</a></td></tr>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    itemlist = []
    for match in matches:
        scrapedtitle = match[1]
        scrapedurl = match[0].replace("&amp;","&").replace("//","/").replace("http:/","http://")
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , folder=True) )

    return itemlist

def episodios(item):
    logger.info("[solidariatv.py] episodios")
    
    # Descarga la página
    data = scrapertools.cachePage(item.url)

    patron  = '<a class="blogsection" href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Último episodio" , action="getvideo" , url=item.url, folder=True) )

    for match in matches:
        scrapedtitle = match[1].strip()
        scrapedurl = match[0].replace("&amp;","&").replace("//","/").replace("http:/","http://")
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="getvideo" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , folder=True) )

    return itemlist

def getvideo(item):
    logger.info("[solidariatv.py] play")

    # Descarga
    data = scrapertools.cachePage(item.url)
    
    patron = '<param name="movie" value="http://www.youtube.com/v/([^\&]+)&'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    try:
        url = matches[0]
    except:
        url = ""

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title=item.title , action="play" , url=url, server = "youtube" , folder=False) )

    return itemlist