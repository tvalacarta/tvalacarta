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
    <div id="post-9924" class="video-item post-9924 post type-post status-publish format-video has-post-thumbnail hentry category-conexion-rioja category-destacados category-programas post_format-post-format-video">
    <div class="item-thumbnail">
    <a href="http://www.populartvlarioja.com/2019/12/conexion-rioja-31-12-19/">
    <img width="480" height="293" src="http://www.populartvlarioja.com/wp-content/uploads/2019/12/conexion-rioja-31-12-19-480x293.jpg" class="attachment-thumb_520x293 size-thumb_520x293 wp-post-image" alt="" />                            <div class="link-overlay fa fa-play"></div>
    </a>
    </div>
    <div class="item-head">
    <h3><a href="http://www.populartvlarioja.com/2019/12/conexion-rioja-31-12-19/" rel="9924" title="Conexión Rioja 31-12-19">Conexión Rioja 31-12-19</a>
    </h3>
    <div class="item-info hidden">
    <span class="item-date">31 diciembre, 2019</span>
    <div class="item-meta">
    </div>
    </div>
    </div>
    <div class="item-content hidden">

    </div>
    <div class="clearfix"></div>
    '''

    # Extrae las zonas de los videos
    patron  = '<div id="post-[^<]+(.*?)<div class="clearfix">'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for bloque in matches:
        title = scrapertools.find_single_match(bloque,'<h3><a href="[^"]+" rel="\d+" title="([^"]+)"')
        url = urlparse.urljoin(item.url, scrapertools.find_single_match(bloque,'<h3><a href="([^"]+)"') )
        thumbnail = scrapertools.find_single_match(bloque,'<img width="\d+" height="\d+" src="([^"]+)"')
        plot = ""

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="play", server="populartvlarioja", show=item.show, folder=False) )

    #<a class="nextpostslink" rel="next" href="http://www.populartvlarioja.com/?cat=8&amp;paged=2">&raquo;</a>
    next_page_url = scrapertools.find_single_match(data,'"nextLink"."([^"]+)"')
    logger.info("tvalacarta.channels.populartvlarioja next_page_url="+next_page_url)
    if next_page_url!="":
        next_page_url = next_page_url.replace("\\","")
        logger.info("tvalacarta.channels.populartvlarioja next_page_url="+next_page_url)
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