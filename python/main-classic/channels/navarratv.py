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
# Canal para Navarra TV
#------------------------------------------------------------

import urlparse,urllib,re

from core import logger
from core import scrapertools
from core.item import Item 

DEBUG = False
__channel__ = "navarratv"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.navarratv mainlist")

    item.url="http://www.natv.es/?c=MATRIZ_LISTADO_BBDD&p=PROGRAMAS"
    item.view="programs"
    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.navarratv programas")    

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    patron  = '<div class="Programa"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)" alt="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapertools.safe_unicode(scrapedtitle).encode("utf-8").strip()
        plot = ""

        itemlist.append( Item(channel=__channel__, action="episodios", title=title, show=title, url=url, thumbnail=thumbnail, fanart=thumbnail, plot=plot, folder=True))

    return itemlist

def detalle_programa(item):
    return item

def episodios(item,load_all_pages=True):
    logger.info("tvalacarta.channels.navarratv episodios")    

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    patron  = '<div class="Programa"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)" alt="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)

        yt_id = scrapertools.find_single_match(scrapedurl,"p=([A-Za-z0-9_\-]+)")
        url = "https://www.youtube.com/watch?v="+yt_id
        title = scrapertools.safe_unicode(scrapedtitle).encode("utf-8").strip()
        plot = ""

        itemlist.append( Item(channel=__channel__, action="play", server="youtube", title=title, url=url, thumbnail=thumbnail, fanart=thumbnail, show=item.show, plot=plot, folder=True))

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
