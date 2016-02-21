# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para Hispan TV
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

__channel__ = "hispantv"
__category__ = "F"
__type__ = "generic"
__title__ = "hispantv"
__language__ = "ES"
__creationdate__ = "20121130"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.hispantv mainlist")

    return categorias(item)

def categorias(item):
    logger.info("tvalacarta.channels.hispantv categorias")    

    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Programas", action="programas", url="http://www.hispantv.com/programas") )
    itemlist.append( Item(channel=__channel__, title="Series", action="programas", url="http://www.hispantv.com/series") )

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.hispantv programas")    

    itemlist = []
    # Descarga la página
    data = scrapertools.cachePage(item.url)
    '''
    <li class="tile col-xs-6 col-sm-3">
    <div class="inner">
    <div class="img video">
    <a href="/showprogram/Cine-a-Contracorriente/107">
    <img data-src="http://217.218.67.233/hispanmedia/files/images/thumbnail/20150215/14592008_m.jpg" alt="Cine a Contracorriente" class="lazy" src="/Views/Assets/img/placeholder.jpg" />
    </a>
    </div>
    <div class="desc">
    <h4><a href="/showprogram/Cine-a-Contracorriente/107">Cine a Contracorriente</a></h4>
    '''
    patron  = '<li class="tile[^<]+'
    patron += '<div class="inner"[^<]+'
    patron += '<div class="img video"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)" alt="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle).strip()
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""

        if item.title=="Series":
            item.category="Series"
        else:
            item.category="Reportajes"

        itemlist.append( Item(channel=__channel__, action="episodios", title=title, show=title, url=url, thumbnail=thumbnail,  plot=plot, viewmode="movie", folder=True))

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.url)
    item.thumbnail = scrapertools.find_single_match(data,'<meta content="([^"]+)" itemprop="thumbnailUrl')

    item.plot = scrapertools.find_single_match(data,'<div class="item-text"><p class="introtext">(.*?)</div>')
    item.plot = scrapertools.htmlclean(item.plot).strip()
    
    return item

def episodios(item):
    logger.info("tvalacarta.channels.hispantv episodios")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    #promo_url = scrapertools.find_single_match(data,'<a href="([^"]+)" class="btn btn-default" target="_blank">Descargar')
    #if promo_url!="":
    #    itemlist.append( Item(channel=__channel__, action="play", server="directo", title="Ver la promo del programa", extra="ignore", url=promo_url, thumbnail=item.thumbnail, plot=item.plot, folder=False))

    #logger.info(data)
    '''
    <li class="tile col-xs-12 col-sm-4">
    <a href="/showepisode/Al-Natural/68Al-Natural---Ensalada-de-Brocoli,-la-Alfalfa,-coctel-de-Tofu-y-Granada,-colirio-de-Eufrasia-y-Aciano-para-ojos/68">
    <div class="inner">
    <div class="img video">
    <img src="http://217.218.67.243/images/thumbnail/20150305/06360563_xl.jpg" alt="Al Natural - Ensalada de Brócoli, la Alfalfa, cóctel de Tofu y Granada, colirio de Eufrasia y Aciano para ojos" />
    '''
    patron  = '<li class="tile[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<div class="inner"[^<]+'
    patron += '<div class="img video"[^<]+'
    patron += '<img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail).replace(" ","%20")
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""
        itemlist.append( Item(channel=__channel__, action="play", title=title, url=url, thumbnail=thumbnail, plot=plot, show=item.show, folder=False))
        
    return itemlist

def detalle_episodio(item):

    data = scrapertools.cache_page(item.url)

    item.plot = scrapertools.htmlclean(scrapertools.find_single_match(data,'<meta content="([^"]+)" itemprop="description')).strip()
    item.thumbnail = scrapertools.find_single_match(data,'<meta content="([^"]+)" itemprop="thumbnailUrl')

    #<meta content="miércoles, 16 de septiembre de 2015 3:30" itemprop="datePublished"
    scrapeddate = scrapertools.find_single_match(data,'<meta content="([^"]+)" itemprop="datePublished')

    item.aired_date = scrapertools.parse_date(scrapeddate)

    item.geolocked = "0"

    media_item = play(item)
    try:
        item.media_url = media_item[0].url.replace("\\","/")
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def play(item):
    logger.info("tvalacarta.channels.hispantv play")

    itemlist = []
    data = scrapertools.cachePage(item.url)
    video_url = scrapertools.find_single_match(data,'<a href="([^"]+)[^>]+>Ver en <i class="icon-youtube')
    if video_url!="":
        itemlist.append( Item(channel=__channel__, action="play", server="youtube", title=item.title, url=video_url, thumbnail=item.thumbnail, plot=item.plot, folder=False))
    else:
        video_url = scrapertools.find_single_match(data,'<a href="([^"]+)" class="btn btn-default" target="_blank">Descargar')
        itemlist.append( Item(channel=__channel__, action="play", server="directo", title=item.title, url=video_url, thumbnail=item.thumbnail, plot=item.plot, folder=False))

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
