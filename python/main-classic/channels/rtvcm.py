# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para rtvcm
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import scrapertools
from core.item import Item
from core import jsontools

DEBUG = False
CHANNELNAME = "rtvcm"
MAIN_URL = "http://www.rtvcm.es/television/programas/"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.rtvcm.mainlist")
    return programas(item)

def programas(item):
    logger.info("tvalacarta.rtvcm.programas")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(MAIN_URL,post="action=filterProgramas&filter=alphab&cat=")
    json_object = jsontools.load_json(data)
    for entry in json_object:
        title = entry["titulo"]
        url = entry["link"]
        thumbnail = ""
        plot = ""
        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url,  thumbnail=thumbnail , action="episodios" , show=title, folder=True) )

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.url)

    item.plot = scrapertools.find_single_match(data,'<meta property="og:description" content="([^"]+)"')

    url = scrapertools.find_single_match(data,'<li><a class="" href="([^"]+)[^>]+>El programa</a></li>')

    if url=="":
        url = item.url

    data = scrapertools.cache_page(url)

    item.thumbnail = scrapertools.find_single_match(data,'<div class="img-container[^<]+<img src="([^"]+)"')
    if item.thumbnail=="":
        item.thumbnail = scrapertools.find_single_match(data,'<div class="box mini-destacado"[^<]+<img src="([^"]+)"')

    return item

def episodios(item):
    logger.info("tvalacarta.rtvcm.episodios")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    page_url = scrapertools.find_single_match(data,'<li><a class="" href="([^"]+)[^>]+>Programas Completos</a></li>')
    
    if page_url=="":
        page_url = scrapertools.find_single_match(data,'<li><a class="" href="([^"]+)[^>]+>Vídeos</a></li>')

    if page_url=="":
        return []

    data = scrapertools.cache_page(page_url)
    logger.info("data="+data)

    bloque = scrapertools.find_single_match(data,'var videos = (\[\{.*?\}\])\;')
    logger.info("bloque=#"+bloque+"#")
    json_object = jsontools.load_json(bloque)

    '''
    if bloque=="":
        #var videos = {"":{"titulo":"CMXM: Washington","fecha":"29\/01\/2016","format_date":"2016-01-29 00:00","descripcion":"","video":"15060","imagen":"http:\/\/api.rtvcm.webtv.flumotion.com\/videos\/15060\/thumbnail.jpg","fecha-publicacion":"1454112600"}};
        bloque = scrapertools.find_single_match(data,'var videos = (\{.*?\})\;')
        bloque = bloque[4:-1]
        logger.info("bloque2=#"+bloque+"#")
        json_object = [jsontools.load_json(bloque)]
    '''

    #[
    #{"titulo":"LCDM: Almendros, Cuenca",
    #"video":"14453",
    #"imagen":"http:\/\/api.rtvcm.webtv.flumotion.com\/videos\/14453\/thumbnail.jpg",
    #"fecha":"16\/10\/2015",
    #"format_date":"2015-10-16 00:00",
    #"descripcion":"","fecha-publicacion":"1445006400"}

    for entry in json_object:
        title = entry["titulo"]+" ("+entry["fecha"]+")"
        url = urlparse.urljoin( page_url , "video-"+str(entry["video"]) )
        thumbnail = entry["imagen"]
        plot = scrapertools.htmlclean(entry["descripcion"])
        aired_date = entry["format_date"]
        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, plot=plot, thumbnail=thumbnail , fanart=thumbnail , action="play" , server="rtvcm", show = item.title , aired_date=aired_date, viewmode="movie_with_plot", folder=False) )

    return itemlist

def detalle_episodio(item):
    logger.info("tvalacarta.rtvcm.detalle_episodio")

    idvideo = scrapertools.find_single_match(item.url,"video-(\d+)$")
    url = "http://api.rtvcm.webtv.flumotion.com/pods/"+idvideo+"?extended=true"
    data = scrapertools.cache_page(url)

    try:
        json_object = jsontools.load_json(data)

        item.thumbnail = json_object["video_image_url"].split("?")[0]
        item.geolocked = "0"
        item.duration = scrapertools.parse_duration_secs( json_object["duration"] )
        item.aired_date = scrapertools.parse_date(item.title)

        from servers import rtvcm as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]

    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def play(item):

    item.server="rtvcm"
    itemlist = [item]

    return itemlist    

def test():

    # Al entrar sale una lista de categorias
    categorias_items = mainlist(Item())
    if len(categorias_items)==0:
        print "No devuelve categorias"
        return False

    programas_items = programas(categorias_items[0])
    if len(programas_items)==0:
        print "No devuelve programas en "+categorias_items[0]
        return False

    episodios_items = episodios(programas_items[0])
    if len(episodios_items)==0:
        print "No devuelve videos en "+programas_items[0].title
        return False

    return True