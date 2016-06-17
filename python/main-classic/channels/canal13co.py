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
# Canal para Canal Trece (Colombia)
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools
import youtube_channel

__channel__ = "canal13co"
__title__ = "canal13co"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.canal13co mainlist")

    item.url="http://www.canaltr3ce.co/programas/"
    item.view="programs"
    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.canal13co programas")    

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    patron  = '<article[^<]+'
    patron += '<div class="portfolio-wrap"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<div class="portfolio-img"[^<]+'
    patron += '<img width="\d+" height="\d+" src="([^"]+)"[^<]+</div.*?'
    patron += '<h5 class="entry-title" itemprop="name">([^<]+)</h5>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapedtitle.strip()
        plot = ""

        itemlist.append( Item(channel=__channel__, action="episodios", title=title, show=title, url=url, thumbnail=thumbnail, fanart=thumbnail, plot=plot, folder=True))

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.url)
    item.plot = scrapertools.find_single_match(data,'<div class="double_space"></div[^<]+<p>([^<]+)</p>')
    item.plot.strip()

    return item

def episodios(item,load_all_pages=True):
    logger.info("tvalacarta.channels.canal13co episodios")

    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data,'<a href="([^"]+)" class="ytcmore"')
    playlist_id = scrapertools.find_single_match(data,"list=([A-Za-z0-9_\-]+)")

    itemlist = youtube_channel.videos( Item(show=item.title,url=playlist_id) )

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
