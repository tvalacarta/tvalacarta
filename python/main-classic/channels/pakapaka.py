# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# tvalacarta 4
# Copyright 2015 tvalacarta@gmail.com
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
# This file is part of tvalacarta 4.
#
# tvalacarta 4 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tvalacarta 4 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tvalacarta 4.  If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------
# XBMC entry point
#------------------------------------------------------------
# Canal para Paka Paka (Argentina)
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "pakapaka"
__title__ = "pakapaka"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.pakapaka mainlist")

    item.url="http://www.pakapaka.gob.ar/videos/dataAjax?pagina=0"
    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.pakapaka programas")    

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    patron  = '<li[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<div class="responsiveThumb ratio16-9" style="background-image. url\(([^\)]+)\)"></div[^<]+'
    patron += '<h3 class="tipo-serie">([^<]+)</h3>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapedtitle
        plot = ""

        itemlist.append( Item(channel=__channel__, action="episodios", title=title, show=title, url=url, thumbnail=thumbnail,  plot=plot, folder=True))

    if len(itemlist)>0:
        current_page = scrapertools.find_single_match(item.url,"pagina\=(\d+)")
        next_page = str( int(current_page)+1 )
        next_page_url = item.url.replace("pagina="+current_page,"pagina="+next_page)
        next_page_item = Item( channel=__channel__ , url=next_page_url)
        itemlist.extend(programas(next_page_item))

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.url)

    item.plot = scrapertools.find_single_match(data,'<meta name="description" content="([^"]+)"')
    item.plot = scrapertools.htmlclean(item.plot).strip()

    return item

def episodios(item,load_all_pages=True):
    logger.info("tvalacarta.channels.pakapaka episodios")
    itemlist = []

    # Descarga la página
    #http://www.pakapaka.gob.ar/series/129334
    if "pagina" in item.url:
        ajax_url = item.url
    else:
        id_serie = scrapertools.find_single_match(item.url,"(\d+)")
        ajax_url = "http://www.pakapaka.gob.ar/series/dataAjax/"+id_serie+"?pagina=0"
    logger.info("tvalacarta.channels.pakapaka episodios ajax_url="+ajax_url)

    data = scrapertools.cache_page(ajax_url)    

    patron  = '<li[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<div class="responsiveThumb ratio16-9" style="background-image. url\(([^\)]+)\)"></div[^<]+'
    patron += '<h3 class="tipo-video">([^<]+)</h3>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapedtitle
        plot = ""
        logger.info("tvalacarta.channels.pakapaka episodios title="+title+", url="+url)

        itemlist.append( Item(channel=__channel__, action="play", server="pakapaka", title=title, show=item.show, url=url, thumbnail=thumbnail,  plot=plot, folder=False))

    if len(itemlist)>0:
        current_page = scrapertools.find_single_match(ajax_url,"pagina\=(\d+)")
        logger.info("tvalacarta.channels.pakapaka episodios current_page="+str(current_page))
        next_page = str( int(current_page)+1 )
        next_page_url = ajax_url.replace("pagina="+current_page,"pagina="+next_page)
        next_page_item = Item( channel=__channel__ , url=next_page_url, show=item.show)
        itemlist.extend(episodios(next_page_item))

    return itemlist

def detalle_episodio(item):

    data = scrapertools.cache_page(item.url)

    item.geolocked = "0"    
    try:
        from servers import pakapaka as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def play(item):

    item.server="pakapaka";
    itemlist = [item]

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
