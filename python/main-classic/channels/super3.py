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
# Canal para Super 3 (Cataluña)
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "super3"
__title__ = "super3"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.super3 mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Sèries en catalá" , url="http://www.ccma.cat/tv3/super3/series/" , action="programas" , folder=True, view="programs") )
    itemlist.append( Item(channel=__channel__, title="Sèries en anglès" , url="http://www.ccma.cat/tv3/super3/english" , action="programas" , folder=True, view="programs") )
    itemlist.append( Item(channel=__channel__, title="Programes" , url="http://www.ccma.cat/Comu/standalone/tv3_super3_videos/contenidor/divgraella_tv3_2/0/0" , action="programas" , folder=True, view="programs") )

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.super3 programas")    

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    patron  = '<div class="F-itemContenidorIntern[^<]+'
    patron += '<a title="([^"]+)" href="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedtitle,scrapedurl,scrapedthumbnail in matches:
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)

        if not "videos/english" in url:
            url = urlparse.urljoin(url,"videos")

        title = scrapedtitle
        plot = ""

        itemlist.append( Item(channel=__channel__, action="episodios", title=title, show=title, url=url, thumbnail=thumbnail, fanart=thumbnail, plot=plot, folder=True))

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.url)

    item.plot = scrapertools.find_single_match(data,'<meta\s*name="description"\s*content="([^"]+)"')
    item.plot = scrapertools.htmlclean(item.plot).strip()

    return item

def episodios(item,load_all_pages=True):
    logger.info("tvalacarta.channels.super3 episodios")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    current_page_url = scrapertools.find_single_match(data,"data-url\s*\=\s*'([^']+)'")
    logger.info("tvalacarta.channels.super3 episodios current_page_url="+current_page_url)

    # No es la primera página, no necesita el paginador
    if "contenidorVideosStandAlone" in item.url:
        current_page_number = scrapertools.find_single_match(item.url,"contenidorVideosStandAlone/(\d+)")
        next_page_number = str( int(current_page_number)+1 )
        current_page_url = item.url

    # Es la primera página, busca la URL de paginación
    elif current_page_url<>"":
        # URL absoluta
        current_page_url = urlparse.urljoin(item.url,current_page_url)
        #http://www.ccma.cat/Comu/standalone/tv3_super3_item_fitxa-programa_videos/contenidor/contenidorVideosStandAlone/1/52276

        current_page_number = "1"
        next_page_number = "2"

        # Fuerza que sea la primera página
        page_number = scrapertools.find_single_match(current_page_url,"contenidorVideosStandAlone/(\d+)")
        current_page_url = current_page_url.replace("contenidorVideosStandAlone/"+page_number,"contenidorVideosStandAlone/1")
        data = scrapertools.cache_page( current_page_url )


    patron = '<article(.*?)</article>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    '''
    <article class="M-destacat super3 T-video  ombres-laterals">
    <a class="media-object" href="/tv3/super3/el-mon-dels-supers/cooperativa-hortgall-de-puigdalber/video/5596632/" title="Cooperativa Hortgall de Puigdàlber">
    <img class="foto" src="http://statics.ccma.cat/multimedia/jpg/7/8/1461325089087.jpg" alt="" />
    <div class="estela"></div>
    <div class="wrapper_txt">
    <div class="icona"></div>                    <div class="txt">                        
    <h2>Cooperativa Hortgall de Puigdàlber</h2>
    </div>
    </div>               
    <div class="gota"></div>   
    </a>   
    </article>
    '''

    for match in matches:
        thumbnail = scrapertools.find_single_match(match,'<img class="foto" src="([^"]+)"')
        url = urlparse.urljoin( item.url , scrapertools.find_single_match(match,'<a class="media-object" href="([^"]+)" title="[^"]+"') )
        title = scrapertools.find_single_match(match,'<a class="media-object" href="[^"]+" title="([^"]+)"')
        plot = ""
        logger.info("tvalacarta.channels.super3 episodios title="+title+", url="+url)

        itemlist.append( Item(channel=__channel__, action="play", server="tv3", title=title, show=item.show, url=url, thumbnail=thumbnail,  plot=plot, folder=False))

    # Si tiene algún elemento, y ha encontrado el paginador, carga la siguiente página
    if len(itemlist)>0 and current_page_url<>"":
        next_page_url = current_page_url.replace("contenidorVideosStandAlone/"+current_page_number,"contenidorVideosStandAlone/"+next_page_number)
        next_page_item = Item( channel=__channel__ , show=item.show, url=next_page_url)
        logger.info("tvalacarta.channels.super3 episodios next_page_url="+next_page_url)
        itemlist.extend(episodios(next_page_item))
    else:
        logger.info("tvalacarta.channels.super3 episodios No hay paginación")

    return itemlist

def detalle_episodio(item):

    data = scrapertools.cache_page(item.url)

    item.geolocked = "0"    
    try:
        from servers import tv3 as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def play(item):

    item.server="tv3";
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
