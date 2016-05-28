# -*- coding: utf-8 -*-
#------------------------------------------------------------------
# tvalacarta
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------------
# Canal para Telemundo, creado por rsantaella
#------------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "telemundo"
__category__ = "L"
__type__ = "generic"
__title__ = "telemundo"
__language__ = "ES"
__creationdate__ = "20130322"
__vfanart__ = ""

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.telemundo mainlist")    
    itemlist = []

    '''
    <div class="grid-collection-item--MAIN">
    <a href="http://www.telemundo.com/novelas/el-fantasma-de-elena/videos" class="grid-collection-item--link">
    <span class="grid-collection-item--aspect-ratio-412x137">
    <img class="grid-collection-item--image" data-original="http://www.telemundo.com/sites/nbcutelemundo/files/styles/show_brand_grid/public/sites/nbcutelemundo/files/images/tv_show/06_ElFantasmaDeElena_596x200_2.jpg?itok=blnz-UOw" width="412" height="137" /><noscript><img class="grid-collection-item--image" src="http://www.telemundo.com/sites/nbcutelemundo/files/styles/show_brand_grid/public/sites/nbcutelemundo/files/images/tv_show/06_ElFantasmaDeElena_596x200_2.jpg?itok=blnz-UOw" width="412" height="137" /></noscript>    </span>
    <span class="grid-collection-item--name">El Fantasma de Elena</span>
    </a>
    </div>
    '''
    data = scrapertools.cachePage("http://msnlatino.telemundo.com/videos/allprograms/")
    patron  = '<div class="grid-collec[^<]+'
    patron += '[^0-9]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<span[^<]+'
    patron += '<img class="[^"]+"[^0-9]+data-original="([^"]+)"[^<]+'
    patron += '<noscript><img[^<]+<\/noscript[^<]+<\/span>[^<]+'
    patron += '<span class="[^"]+">([^<]+)<\/span>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        thumbnail = scrapedthumbnail
        url = scrapedurl.replace("videos","capitulos")
        itemlist.append( Item(channel=__channel__, action="episodios", title=title, url=url, thumbnail=thumbnail,  viewmode="movie", folder=True))

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.telemundo episodios")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    patron = "<article(.*?)</article>"
    matches = re.compile(patron,re.DOTALL).findall(data)

    for match in matches:
        logger.info("match="+match)
        title = scrapertools.find_single_match(match,'<a href="[^"]+" class="episode-grid-item--episode-number">([^<]+)</a>')
        url = scrapertools.find_single_match(match,'<a href="([^"]+)" class="episode-grid-item--episode-number')
        thumbnail = scrapertools.find_single_match(match,'data-original="([^"]+)"')
        plot = scrapertools.find_single_match(match,'<div class="episode-grid-item--promotional-description">([^<]+)</div>')
        itemlist.append( Item(channel=__channel__, action="partes", title=title, url=url, thumbnail=thumbnail, fanart=thumbnail, plot=plot, viewmode="movie_with_plot", folder=True))

    return itemlist

def partes(item):
    #http://www.telemundo.com/novelas/2013/09/16/bella-calamidades-capitulo-1-parte-1-de-9-video-telemundo-novelas?part=0
    
    logger.info("tvalacarta.channels.telemundo partes")
    itemlist = []

    itemlist.append( Item(channel=__channel__, action="play", server="telemundo", title="Parte 1", url=item.url, folder=False))

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    #<li class="player--nav-item"><a href="http://www.telemundo.com/novelas/2013/09/16/bella-calamidades-capitulo-1-parte-1-de-9-video-telemundo-novelas?part=1" class="player--nav-number active">2</a>
    #<li class="player--nav-item"><a href="http://www.telemundo.com/novelas/2013/09/16/bella-calamidades-capitulo-1-parte-1-de-9-video-telemundo-novelas?part=1" class="player--nav-number active">2</a>    </li>
    patron = '<li class="player--nav-item"[^<]+'
    patron += '<a href="([^"]+)" class="player--nav-number active">([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    logger.info("matches="+repr(matches))

    for scrapedurl,scrapedtitle in matches:
        title = "Parte "+str(scrapedtitle)
        url = scrapedurl
        itemlist.append( Item(channel=__channel__, action="play", server="telemundo", title=title, url=url, folder=False))

    return itemlist
