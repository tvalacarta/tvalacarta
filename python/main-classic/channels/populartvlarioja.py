# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Popular TV (La Rioja)
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "populartvlarioja"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.populartvlarioja mainlist")

    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.populartvlarioja canal")

    item.url = "http://www.populartvlarioja.com/?cat=7"

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data,'<a[^>]+>Programas</a[^<]+<ul class="sub-menu">(.*?)</ul')
    
    '''
    <a href="http://www.populartvlarioja.com/?cat=7">Programas</a>
    <ul class="sub-menu">
    <li id="menu-item-43" class="menu-item menu-item-type-taxonomy menu-item-object-category menu-item-43"><a href="http://www.populartvlarioja.com/?cat=8">Marcador</a></li>
    <li id="menu-item-3070" class="menu-item menu-item-type-taxonomy menu-item-object-category menu-item-3070"><a href="http://www.populartvlarioja.com/?cat=26">Mano a Mano</a></li>
    <li id="menu-item-3071" class="menu-item menu-item-type-taxonomy menu-item-object-category menu-item-3071"><a href="http://www.populartvlarioja.com/?cat=24">A solas con Ana</a></li>
    <li id="menu-item-46" class="menu-item menu-item-type-taxonomy menu-item-object-category menu-item-46"><a href="http://www.populartvlarioja.com/?cat=11">La Rioja y Cía</a></li>
    <li id="menu-item-634" class="menu-item menu-item-type-taxonomy menu-item-object-category menu-item-634"><a href="http://www.populartvlarioja.com/?cat=20">La vuelta a la Rioja en 80 días</a></li>
    </ul>
    '''

    # Extrae las zonas de los programas
    patron  = '<li[^<]+<a href="([^"]+)">([^<]+)</a></li>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = ""
        plot = ""

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="episodios", show=title, folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.populartvlarioja episodios")

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)

    '''
    <div id="post-3731" class="post-3731 post type-post status-publish format-standard has-post-thumbnail hentry category-marcador category-programas item cf item-video">
    <div class="thumb">
    <a class="clip-link" data-id="3731" title="Marcador 20-11-17" href="http://www.populartvlarioja.com/?p=3731">
    <span class="clip">
    <img src="http://www.populartvlarioja.com/wp-content/uploads/2017/11/marcador-20-11-17.jpg" alt="Marcador 20-11-17" /><span class="vertical-align"></span>
    '''

    # Extrae las zonas de los videos
    patron  = '<div id="post-[^<]+'
    patron += '<div class="thumb"[^<]+'
    patron += '<a class="clip-link" data-id="[^"]+" title="([^"]+)" href="([^"]+)"[^<]+'
    patron += '<span class="clip"[^<]+'
    patron += '<img src="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedtitle,scrapedurl,scrapedthumbnail in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail
        plot = ""

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="play", server="populartvlarioja", show=item.show, folder=False) )

    #<a class="nextpostslink" rel="next" href="http://www.populartvlarioja.com/?cat=8&amp;paged=2">&raquo;</a>
    next_page_url = scrapertools.find_single_match(data,'<a class="nextpostslink" rel="next" href="([^"]+)"')
    if next_page_url!="":
        next_page_url = next_page_url.replace("&amp;","&")
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