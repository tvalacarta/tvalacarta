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
import urlparse,urllib2

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

URL_LIVE  = "http://streaming.8tv.cat/8TV/8aldia-directe/chunklist_w1058883651.m3u8"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.vuittv mainlist")

    itemlist = []

    itemlist.append( Item(channel=__channel__, title="En directe",               action="play",         url = URL_LIVE, folder=False) )
    itemlist.append( Item(channel=__channel__, title="8 al dia",                 action="episodios",    url="http://www.8tv.cat/programa/8aldia/", thumbnail="http://www.8tv.cat/wp-content/uploads/2017/08/banner_8aldia.jpg", plot="Jordi Armenteras està al capdavant del nou 8 al dia. Cada vespre, és la cara de l’actualitat en un renovat format televisiu que combina la informació i l’anàlisi. Un salt endavant per reforçar debats i tertúlies amb la presència de periodistes i d’opinadors que són referent al país.") )
    itemlist.append( Item(channel=__channel__, title="Arucitys",                 action="episodios",    url="http://www.arucitys.com/a_la_carta", thumbnail="http://www.8tv.cat/wp-content/uploads/2012/02/banner_arus.jpg", plot="A l’Arucitys tot és bon humor. És la manera més divertida d’estar al corrent de tota l’actualitat, del món del cor i  de la televisió. Per això, després de 16 anys i més de 3.000 programes en directe, s’ha convertit en un referent de les sobretaules catalanes, i cada dia hi ha més gent enganxada a aquest magazín.") )
    itemlist.append( Item(channel=__channel__, title="Catalunya Directe",        action="episodios",    url="http://www.8tv.cat/programa/catalunya-directe/", thumbnail="http://www.8tv.cat/wp-content/uploads/2017/08/banner_catDirecte.jpg", plot="Un programa d’actualitat per redescobrir Catalunya de la mà de Quim Morales i d’un bon grapat de reporters repartits arreu del territori.") )
    itemlist.append( Item(channel=__channel__, title="Fora de joc",              action="episodios",    url="http://www.8tv.cat/programa/fora-de-joc/", thumbnail="http://www.8tv.cat/wp-content/uploads/2017/08/banner_forajoc.jpg", plot="Fora de joc, amb Aleix Parisé, és un magazín esportiu que repassa diàriament l’actualitat dels tres equips catalans de primera divisió: Barça, Espanyol i Girona, així com les notícies esportives més importants que puguin sorgir al llarg del dia.") )
    itemlist.append( Item(channel=__channel__, title="La nit a 8tv",             action="episodios",    url="http://www.8tv.cat/programa/la-nit-a-8tv/", thumbnail="http://www.8tv.cat/wp-content/uploads/2018/04/banner_nita8tv.png", plot="La nit a 8tv és un espai informatiu dirigit i presentat per Ramon Rovira que repassa les claus del dia, mitjançant debats, entrevistes i cara a cara.") )

    return itemlist

def directos(item=None):
    logger.info("tvalacarta.channels.vuittv directos")

    itemlist = []

    itemlist.append( Item(channel=__channel__, title="8 TV",        url=URL_LIVE, thumbnail="http://media.tvalacarta.info/canales/128x128/ochotv.png", category="Locales", action="play", folder=False ) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.8tv episodios")

    if "arucitys" in item.url:
        return episodios_arucitys(item)

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
    patron += '<span id="ch\d+-youtube">([0-9A-Za-z_-]{11})'
    matches = scrapertools.find_multiple_matches(data,patron)

    for scrapedtitle,scrapeddate1,scrapedplot,scrapeddate2,value1,value2,youtube_id in matches:
        #youtube_id = scrapertools.find_single_match(scrapedurl,"embed\/([0-9A-Za-z_-]{11})")
        #https://i.ytimg.com/vi_webp/ed5e4AHFsJA/sddefault.webp
        youtube_thumbnail = "https://i.ytimg.com/vi_webp/"+youtube_id+"/sddefault.webp"
        youtube_url = "https://www.youtube.com/watch?v="+youtube_id
        itemlist.append(Item(channel=__channel__, action = 'play', server="youtube", title=scrapedtitle, url=youtube_url, thumbnail=youtube_thumbnail, folder=False) )

    return itemlist

def episodios_arucitys(item):
    logger.info("tvalacarta.channels.8tv episodios_arucitys")

    itemlist = []

    data = scrapertools.cache_page(item.url)

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

    patron  = '\{"pageId"\:"[^"]+","title"\:"([^"]+)","pageUriSEO"\:"([^"]+)"'
    matches = scrapertools.find_multiple_matches(data,patron)

    for scrapedtitle,scrapedurl in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        aired_day = scrapertools.find_single_match(scrapedtitle,"(\d+)-\d+-\d+")
        aired_month = scrapertools.find_single_match(scrapedtitle,"\d+-(\d+)-\d+")
        aired_year = scrapertools.find_single_match(scrapedtitle,"\d+-\d+-(\d+)")
        if len(aired_year)==2:
            aired_year = "20"+aired_year

        aired_date = aired_year+"-"+aired_month+"-"+aired_day

        itemlist.append(Item(channel=__channel__, action = 'play', server="vuittv", title=scrapedtitle, url=url, aired_date=aired_date, folder=False) )

    itemlist = sorted(itemlist, key=lambda i: i.aired_date, reverse=True)

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    # Comprueba que la primera opción tenga algo
    programas_itemlist = mainlist(Item())
    episodios_itemlist = episodios(programas_itemlist[1])

    if len(episodios_itemlist)==0:
        return False,"No hay episodios en "+programas_itemlist[1].title

    episodios_itemlist = episodios_arucitys(programas_itemlist[2])

    if len(episodios_itemlist)==0:
        return False,"No hay episodios en "+programas_itemlist[2].title

    from servers import vuittv as server
    video_urls = server.get_video_url(episodios_itemlist[0].url)

    if len(video_urls)==0:
        return False,"No funciona el vídeo "+episodios_itemlist[0].title+" en "+programas_itemlist[2].title

    # Verifica los directos
    directos_itemlist = directos(Item())

    for directo_item in directos_itemlist:

        try:
            data = scrapertools.cache_page(directo_item.url)
        except:
            return False,"Falla el canal en directo "+directo_item.title

    return True,""
