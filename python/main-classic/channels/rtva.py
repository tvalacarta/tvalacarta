# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para RTVA
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib,re

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "rtva"
MAIN_URL = "http://www.canalsur.es/programas_tv.html"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.rtva mainlist")
    
    return programas(item)

def programas(item, load_all_pages=False):
    logger.info("tvalacarta.channels.rtva programas")

    if item.url=="":
        item.url = MAIN_URL
    
    itemlist=[]

    # Extrae los programas

    intentos = 0
    while intentos<5:
        data = scrapertools.cache_page(item.url)
        logger.info("tvalacarta.channels.rtva programas data="+data)

        bloque = scrapertools.find_single_match(data,'<ul class="programas_list_az cpaseccionl">(.*?)</ul>')
        logger.info("tvalacarta.channels.rtva programas bloque="+bloque)

        if bloque=="":
            logger.info("tvalacarta.channels.rtva lista vacia, reintentando...")
            intentos = intentos + 1
            import time
            time.sleep(2)
        else:
            break

    patron  = '<a href="([^"]+)"[^<]+'
    patron += "<img src='([^']+)'[^<]+</a[^<]+"
    patron += '</div[^<]+'
    patron += '<div[^<]+'
    patron += '<h5[^<]+<a[^>]+>([^<]+)</a></h5[^<]+'
    patron += '<div class="programs_list_az_item_description">([^<]+)</div>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedplot in matches:
        title = scrapedtitle.strip()
        url = scrapedurl
        thumbnail = scrapedthumbnail
        plot = scrapertools.htmlclean(scrapedplot.strip())
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="episodios" , url=url, thumbnail=thumbnail, fanart=thumbnail, plot=plot , show=title, viewmode="movie_with_plot") )

    #<a href="http://www.canalsuralacarta.es/television/listado/todos/2" class="enlace siguiente" rel="contenido_main#program_list">siguiente</a>
    next_page_url = scrapertools.find_single_match(data,'class="enlace activa[^<]+</a[^<]+<a href="([^"]+)"')
    if next_page_url!="":
        next_page_item = Item(channel=CHANNELNAME, title=">> Página siguiente" , action="programas" , url=urlparse.urljoin(item.url,next_page_url) )

        if load_all_pages:
            itemlist.extend(programas(next_page_item,load_all_pages))
        else:
            itemlist.append(next_page_item)

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.page)

    item.plot = scrapertools.find_single_match(data,'<div class="textoPrograma">(.*?)</div>')
    item.plot = scrapertools.htmlclean(item.plot).strip()

    #item.title = scrapertools.find_single_match(data,'<article class="span8"[^<]+<h2>([^<]+)</h2>')

    return item

def episodios(item, load_all_pages=False):
    logger.info("tvalacarta.channels.rtva episodios")

    # Descarga la página
    intentos = 0
    while intentos<5:
        data = scrapertools.cachePage(item.url)
        data = scrapertools.find_single_match(data,'<section id="mas_programas" class="slider">(.*?)</section>')
        logger.info("data="+data)
        if data=="":
            intentos = intentos + 1
            import time
            time.sleep(2)
        else:
            break

    patron  = '<img src="([^"]+)"[^<]+'
    patron += '<div class="playP"[^<]+'
    patron += '</div[^<]+'
    patron += '</div[^<]+'
    patron += '<div class="fecha hidde[^>]+>([^<]+)</div[^<]+'
    patron += '<span class="titulo">([^<]+)</span><br[^<]+'
    patron += '<div class="descripcion[^>]+>([^<]*)</div[^<]+'
    patron += '<div class="fecha_hora hidden">([^<]+)</div[^<]+'
    patron += '<div class="video[^>]+>([^<]+)</div>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    itemlist = []
    for scrapedthumbnail,fecha,scrapedtitle,scrapedplot,fechahora,media_url in matches:
        try:
            dia = " ("+fecha.split(" ")[1]+")"
        except:
            try:
                dia = " ("+fechahora.split(" ")[0]+")"
            except:
                dia = ""
        title = scrapedtitle + dia
        url = item.url
        thumbnail = scrapedthumbnail
        plot = scrapedplot
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="play" , url=url, page=url , thumbnail=thumbnail, fanart=thumbnail, plot=plot , extra=media_url, show=item.show , folder=False, viewmode="movie_with_plot") )

    return itemlist

def detalle_episodio(item):

    item.aired_date = scrapertools.parse_date(item.title)
    item.geolocked = "0"
    item.media_url = item.extra

    return item

def play(item,page_data=""):
    logger.info("tvalacarta.channels.rtva play")

    itemlist = []

    if item.extra<>"":
        itemlist.append( Item(channel=CHANNELNAME, title=item.title , action="play" , server="directo" , url=item.extra, thumbnail=item.thumbnail, plot=item.plot , show=item.show , folder=False) )

    return itemlist

def test():

    programas_items = mainlist(Item())
    if len(programas_items)==0:
        print "No devuelve programas en "+categorias_items[0]
        return False

    episodios_items = episodios(programas_items[0])
    if len(episodios_items)==1:
        print "No devuelve videos en "+programas_items[0].title
        return False

    return True