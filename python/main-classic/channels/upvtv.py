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
# Canal para UPV TV
#------------------------------------------------------------

import urlparse,urllib,re

from core import logger
from core import scrapertools
from core.item import Item 

DEBUG = False
CHANNELNAME = "upvtv"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.upvtv mainlist")

    item.url="http://www.upv.es/rtv/tv/carta"
    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.upvtv programas")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    patron = '<ul data-categoria(.*?)</ul>'
    bloques = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(bloques)

    for bloque in bloques:

        patron  = '<li(.*?)</li'
        matches = re.compile(patron,re.DOTALL).findall(bloque)
        if DEBUG: scrapertools.printMatches(matches)

        for match in matches:
            title = scrapertools.find_single_match(match,'title="([^"]+)"')
            if title=="":
                title = scrapertools.find_single_match(match,'<a[^>]+>([^<]+)</a>')
            title = title.decode('iso-8859-1').encode("utf8","ignore")
            thumbnail = scrapertools.find_single_match(match,'<img.*?src="([^"]+)"')
            plot = scrapertools.find_single_match(match,'<span class="tex_imagen"[^<]+<br />([^<]+)</span>')
            url = scrapertools.find_single_match(match,'a href="([^"]+)"')
            url = urlparse.urljoin(item.url,url)
            if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
            itemlist.append( Item( channel=CHANNELNAME , title=title , action="episodios" , url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=True ) )

    return itemlist

def detalle_programa(item):
    data = scrapertools.cachePage(item.url)

    item.plot = scrapertools.find_single_match(data,'<p class="categoria">([^<]+)</p>')
    item.plot = item.plot + " " + scrapertools.find_single_match(data,'<p id="pro_desc">([^<]+)"<')
    item.plot = scrapertools.htmlclean(item.plot).strip()

    if item.thumbnail=="":
        item.thumbnail = scrapertools.find_single_match(data,'<div class="t1"><img src="([^"]+)"')
    if item.thumbnail=="":
        item.thumbnail = scrapertools.find_single_match(data,'<meta property="og:image" content="([^"]+)"')

    return item

def episodios(item):
    logger.info("tvalacarta.channels.upvtv episodios")
    itemlist=[]

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.find_single_match(data,'<h1>Programas anteriores(.*?)</ul')

    # Extrae los capitulos
    patron  = '<li[^<]+'
    patron += '<span class="enlace"><a href="([^"]+)" >([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.replace("\n"," ")
        title = re.compile("\s+",re.DOTALL).sub(" ",title)
        title = title.decode('iso-8859-1').encode("utf8","ignore")
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        aired_date = scrapertools.parse_date(title)

        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=CHANNELNAME , title=title , action="play" , server="upvtv" , url=url , thumbnail=thumbnail , plot=plot , show=item.show , fanart=thumbnail , aired_date=aired_date, folder=False ) )

    return itemlist

def detalle_episodio(item):

    item.geolocked = "0"
    
    try:
        from servers import upvtv as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    # Todas las opciones tienen que tener algo
    programas_items = mainlist(Item())
    if len(programas_items)==0:
        return False

    episodios_items = episodios(programas_items[0])
    if len(episodios_items)==0:
        return False

    return bien
