# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Canal 13 (Chile)
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "trececl"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.trececl mainlist")

    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.trececl canal")

    item.url = "http://www.13.cl/"

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    
    '''
    <div class="swiper-slide">
    <a href="/programas/vertigo-t5" title="Vértigo">
    <img data-image data-desktop="http://static.13.cl/7/sites/default/files/styles/260x150/public/programas/configuracion/field-imagen/vertigo-t5-640x360.jpg?itok=XHJLUY_g" width="260" height="146"></a></div>        
    '''

    # Extrae las zonas de los programas
    patron  = '<div class="swiper-slide"[^<]+'
    patron += '<a href="([^"]+)" title="([^"]+)"[^<]+'
    patron += '<img data-image data-desktop="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url,scrapedurl)+"/capitulos"
        thumbnail = scrapedthumbnail
        plot = ""

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="episodios", show=title, folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.trececl episodios")

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)

    '''
    <article itemscope itemtype="http://schema.org/Article" class="news news-box">
    <figure itemprop="image" itemtype="http://schema.org/ImageObject" class="news-media">
    <a href="/programas/kosem/capitulos/capitulo-58-un-nuevo-sultan" title="Capítulo 58 / Un nuevo Sultán">
    <img src="http://static.13.cl/7/sites/all/themes/portal/resources/images/lazyload.gif" data-image data-desktop="http://static.13.cl/7/sites/default/files/styles/356x201/public/programas/articulos/field-imagen/0501-cap-kosem.jpg?itok=x6jAMoWG" alt="Capítulo 58 / Un nuevo Sultán" width="356" height="201" itemprop="contentUrl">
    <span class="video-duration">01:15:23</span><span class="play"></span>
    </a>
    </figure>
    <div class="news-data">
    <a href="/programas/kosem/capitulos/capitulo-58-un-nuevo-sultan" title="01 de mayo " class="news-section">01 de mayo </a>
    <h1 itemprop="name headline" class="news-title"><a href="/programas/kosem/capitulos/capitulo-58-un-nuevo-sultan" title="Capítulo 58 / Un nuevo Sultán" itemprop="url">Capítulo 58 / Un nuevo Sultán</a></h1>
    </div>
    </article>
    '''

    # Extrae las zonas de los videos
    patron  = '<article[^<]+'
    patron += '<figure[^<]+'
    patron += '<a href="([^"]+)" title="([^"]+)"[^<]+'
    patron += '<img src="[^"]+" data-image data-desktop="([^"]+)"[^<]+'
    patron += '<span class="video-duration">([^<]+)</span>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle,scrapedthumbnail,scrapeduration in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail
        plot = ""

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="play", server="trececl", show=item.show, folder=False) )

    next_page_url = scrapertools.find_single_match(data,'<ul class="pager pager-load-more"><li class="pager-next first last"><a href="([^"]+)">Ver m')
    if next_page_url!="":
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page_url), action="episodios", show=item.show, folder=True) )

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    # Comprueba que la primera opción tenga algo
    categorias_items = mainlist(Item())
    programas_items = programas(categorias_items[0])
    episodios_items = episodios(programas_items[0])

    if len(episodios_items)>0:
        return True

    return False