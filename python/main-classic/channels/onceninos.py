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
# Canal para Once Niños (México)
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "onceninos"
__title__ = "onceninos"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.onceninos mainlist")

    item.url="http://canalonce.mx/onceninos/ninos2/?vod"
    item.view="programs"
    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.onceninos programas")    

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    patron  = '<div class="entry small"[^<]+'
    patron += '<div class="thumbnail"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)"[^<]+<span class="overlay"></span[^<]+'
    patron += '</a[^<]+'
    patron += '</div[^<]+<!--[^<]+'
    patron += '<h2 class="title"><a[^>]+>([^<]+)</a></h2[^<]+'
    patron += '<div class="entry-content"[^<]+'
    patron += '<div class="bottom-bg"[^<]+'
    patron += '<div class="excerpt"[^<]+'
    patron += '<p>([^<]+)</p>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedplot in matches:
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapedtitle.strip()
        plot = scrapedplot.strip()

        itemlist.append( Item(channel=__channel__, action="episodios", title=title, show=title, url=url, thumbnail=thumbnail, fanart=thumbnail, plot=plot, folder=True))

    return itemlist

def detalle_programa(item):
    return item

def episodios(item,load_all_pages=True):
    logger.info("tvalacarta.channels.onceninos episodios")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data,'Más episodios de(.*?)</ul>')    

    patron  = '<li[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<div class="episodelist" style="background-image.url\(([^\)]+)\)[^<]+'
    patron += '<img[^<]+'
    patron += '</div[^<]+'
    patron += '<p align="center">([^<]+)</p>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapedtitle
        plot = ""
        logger.info("tvalacarta.channels.onceninos episodios title="+title+", url="+url)

        itemlist.append( Item(channel=__channel__, action="play", server="onceninos", title=title, show=item.show, url=url, thumbnail=thumbnail,  plot=plot, folder=False))

    return itemlist

def detalle_episodio(item):

    data = scrapertools.cache_page(item.url)
    item.title = scrapertools.find_single_match(data,'<p id="title">([^<]+)</p>')
    item.aired_date = scrapertools.parse_date(item.title)
    item.plot = scrapertools.find_single_match(data,'<p id="desp">([^<]+)</p>')

    item.geolocked = "0"    
    try:
        from servers import onceninos as servermodule
        video_urls = servermodule.get_video_url(item.url,page_data=data)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def play(item):

    item.server="onceninos";
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
