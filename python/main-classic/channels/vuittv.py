# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para 8TV
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import re
import sys
import os
import traceback
import urllib2

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "vuittv"
__category__ = "R"
__type__ = "generic"
__title__ = "8TV"
__language__ = "ES"
__creationdate__ = "20160928"

DEBUG = config.get_setting("debug")

URL_LIVE  = "rtmp://streaming.8tv.cat:1935/8TV?videoId=3998198240001&lineUpId=&pubId=1589608506001&playerId=1982328835001&affiliateId=/8aldia-directe?videoId=3998198240001&lineUpId=&pubId=1589608506001&playerId=1982328835001&affiliateId="

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.8tv mainlist")

    itemlist = []

    itemlist.append( Item(channel=__channel__, title="En directe",               action="play",         url = URL_LIVE,                                            folder=False) )
    itemlist.append( Item(channel=__channel__, title="Catalunya Directe",        action="episodios",    url="http://www.8tv.cat/programa/catalunya-directe/") )
    #itemlist.append( Item(channel=__channel__, title="Arucitys",                 action="episodios_a",  url="http://www.arucitys.com/") )
    itemlist.append( Item(channel=__channel__, title="8 al dia",                 action="episodios",    url="http://www.8tv.cat/programa/8aldia/") )
    itemlist.append( Item(channel=__channel__, title="Fora de joc",              action="episodios",    url="http://www.8tv.cat/programa/fora-de-joc/") )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.8tv episodios")

    itemlist = []

    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data,'<ul id="playlist-chapters">(.*?)</ul>')

    '''
    <h4><a href="#" id="ch24721" class="ch-link" title="Catalunya directe #15">Catalunya directe #15</a></h4>
    <span class="date">25/09/17</span>
    <p></p>
    <div class="ch-data">
    <span id="ch24721-desc"></span>
    <span id="ch24721-time">25/09/2017 07.09</span>
    <span id="ch24721-video"></span>
    <span id="ch24721-brightcove">S1x2LLY6OW</span>
    <span id="ch24721-youtube"><iframe width="640" height="360" src="https://www.youtube.com/embed/Rfc70h4K6SE?feature=oembed" 
    '''

    patron  = '<h4><a[^>]+>([^<]+)</a></h4[^<]+'
    patron += '<span class="date">([^<]+)</span[^<]+'
    patron += '<p></p[^<]+'
    patron += '<div class="ch-data"[^<]+'
    patron += '<span id="ch\d+-desc">([^<]*)</span[^<]+'
    patron += '<span id="ch\d+-time">([^<]*)</span[^<]+'
    patron += '<span id="ch\d+-video">([^<]*)</span[^<]+'
    patron += '<span id="ch\d+-brightcove">([^<]*)</span[^<]+'
    patron += '<span id="ch\d+-youtube"><iframe width="\d+" height="\d+" src="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data,patron)

    for scrapedtitle,scrapeddate1,scrapedplot,scrapeddate2,value1,value2,scrapedurl in matches:
        youtube_id = scrapertools.find_single_match(scrapedurl,"embed\/([0-9A-Za-z_-]{11})")
        #https://i.ytimg.com/vi_webp/ed5e4AHFsJA/sddefault.webp
        youtube_thumbnail = "https://i.ytimg.com/vi_webp/"+youtube_id+"/sddefault.webp"
        youtube_url = "https://www.youtube.com/watch?v="+youtube_id
        itemlist.append(Item(channel=__channel__, action = 'play', server="youtube", title=scrapedtitle, url=scrapedurl, thumbnail=youtube_thumbnail, folder=False) )

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    # Comprueba que la primera opción tenga algo
    items = mainlist(Item())
    section = loadsections(items[1])

    if len(section)==0:
        return False,"No hay videos en portada"

    section = loadprogram(items[4])

    if len(section)==0:
        return False,"No hay videos en 8aldia"

    return True,""
