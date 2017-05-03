# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Canal 22 (México)
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import config
from core import logger
from core import scrapertools
from core import jsontools
from core.item import Item

DEBUG = config.get_setting("debug")
CHANNELNAME = "canal22"
PROGRAMAS_URL = "http://canal22.org.mx/alacarta/"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.canal22 mainlist")

    return programas(Item(channel=CHANNELNAME))

def programas(item):
    logger.info("tvalacarta.channels.canal22 programas")

    itemlist = []

    if item.url=="":
        item.url=PROGRAMAS_URL

    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data,'<section class="int_programas">(.*?)</section')

    patron  = '<a href="([^"]+)"[^<]+'
    patron += '<div class="programas"[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '<div class="tit">([^<]+)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = unicode( scrapedtitle.strip() , "iso-8859-1" , errors="ignore").encode("utf-8")
        thumbnail = scrapedthumbnail
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="episodios", url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail, view="videos" ) )

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.page)

    item.plot = scrapertools.find_single_match(data,'<article class="span8"[^<]+<div class="contenido_noticia">(.*?)</div>')
    item.plot = scrapertools.htmlclean(item.plot).strip()

    item.thumbnail = scrapertools.find_single_match(data,'<img src="([^"]+)" alt="" class="img-det-not">')

    #item.title = scrapertools.find_single_match(data,'<article class="span8"[^<]+<h2>([^<]+)</h2>')

    return item

def episodios(item):
    logger.info("tvalacarta.channels.canal22 episodios")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    '''
    <a class="itemgo" href="?c=d&p=13&n=0_uq0p39bt&ti=33">
    <div class="programas" cap="214">
    <img src="http://cdn.kaltura.com/p/1768131/sp/176813100/thumbnail/entry_id/0_uq0p39bt/width/256/height/154">
    <div class="tit">Basura urbana</div>
    '''

    patron  = '<a class="itemgo" href="([^"]+)"[^<]+'
    patron += '<div class="programas"[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '<div class="tit">([^<]+)</div'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = unicode( scrapedtitle.strip() , "iso-8859-1" , errors="ignore").encode("utf-8")
        thumbnail = scrapedthumbnail
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="play", server="canal22", url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail, folder=False ) )

    return itemlist

def detalle_episodio(item):

    item.geolocked = "0"
    
    try:
        from servers import canal22 as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def play(item):

    item.server="canal22";
    itemlist = [item]

    return itemlist

# Test de canal
# Devuelve: Funciona (True/False) y Motivo en caso de que no funcione (String)
def test():
    
    # Carga el menu principal
    items_programas = mainlist(Item())

    if len(items_programas)==0:
        return False,"No hay programas"

    for item_programa in items_programas:
        items_episodios = episodios(item_programa)
        if len(items_episodios)>0:
            break

    if len(items_episodios)==0:
        return False,"No hay episodios"

    item_episodio = detalle_episodio(items_episodios[0])
    if item_episodio.media_url=="":
        return False,"El conector no devuelve enlace para el vídeo "+item_episodio.title

    return True,""
