# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para dplay
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import re, urllib, urlparse

from core import logger
from core import scrapertools
from core import config
from core.item import Item
from servers import servertools

logger.info("tvalacarta.channels.dplay init")

DEBUG = False
CHANNELNAME = "dplay"


def isGeneric():
    return True


def mainlist(item):
    logger.info("tvalacarta.channels.dplay mainlist")
    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Series", action="programas", url="http://es.dplay.com/series/", folder=True) )
    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.dplay programas")

    itemlist = []
    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data, '<h1 class="margin_left">Lista de programas A-Z</h1>(.*?)<div class="clear"></div>')
    
    patron = '<li><a href="([^"]+)">([^<]+)</a>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedtitle in matches:
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle, action="temporadas", url=urlparse.urljoin(item.url,scrapedurl), show=scrapedtitle, folder=True) )

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.url)
    item.plot = scrapertools.find_single_match(data, '<meta property="og.description"\s+content="(.*?)"')
    item.thumbnail = scrapertools.find_single_match(data, '<meta property="og.image"\s+content="(.*?)"')

    return item

def temporadas(item):
    logger.info("tvalacarta.channels.dplay temporadas")

    itemlist = []
    data = scrapertools.cache_page(item.url)

    patron  = '<div class="episode_carousel"[^<]+'
    patron += '<h2 class="carousel-title">([^<]+)</h2>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedtitle in matches:
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle, action="episodios", url=urlparse.urljoin(item.url,"episodios/"+scrapertools.slugify(scrapedtitle)), show=item.show, folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.dplay episodios")

    itemlist = []

    '''
    <li class="single_episode_element episode-slide ">
    <a href="/dmax/en-mitad-de-la-nada/temporada-1-episodio-14-regreso-a-la-veta-principal/">
    <div class="caros-ep-duration animated_delayed">
    <div class="container_clock" data-duration='44'></div>
    <p class="animated_delayed" data-duration='44'>44 min</p>
    </div>
    <figure class="caros-ep-img-container animated_delayed">

    <img class="img-responsive" src="https://dplay-south-prod-images.disco-api.com/2017/01/18/videoasset-16577-1506071092087.jpg?w=480&f=jpg&p=true&q=75" alt="" />
    </figure>

    <figcaption>
    <h4 class="caros-show-title">En mitad de la nada</h4>
    <h5 class="caros-ep-title">Regreso a la veta principal </h5>
    </figcaption>
    <span class="play_cta">
    <div class="triangle_css animated_delayed"></div>
    play  
    </span>
    <span class="published_date  old_content ">18/01/2017</span>
    </a>
    </li>
    '''

    patron  = '<li class="single_episode_element episode-slide[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<div class="caros-ep-duration animated_delayed"[^<]+'
    patron += '<div class="container_clock" data-duration=\'(\d+)\'></div[^<]+'
    patron += '<p class="animated_delayed"[^>]+>[^<]+</p[^<]+'
    patron += '</div[^<]+'
    patron += '<figure class="caros-ep-img-container animated_delayed"[^<]+'
    patron += '<img class="img-responsive" src="([^"]+)" alt="" />
    patron += '</figure>
    patron += '<figcaption>
    patron += '<h4 class="caros-show-title">En mitad de la nada</h4>
    patron += '<h5 class="caros-ep-title">Regreso a la veta principal </h5>
    patron += '</figcaption>
    patron += '<span class="play_cta">
    patron += '<div class="triangle_css animated_delayed"></div>
    patron += 'play  
    patron += '</span>
    patron += '<span class="published_date  old_content ">18/01/2017</span>
    patron += '</a>
    patron += '</li>

    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot in matches:
        scrapedurl = item.url + scrapedurl
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle, action="play", url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, fanart=fanart, show=item.show, folder=False) )

    if len(itemlist) < 2:
        itemlist.append( Item(channel=CHANNELNAME, title="No hay episodios completos disponibles", action="", url="", thumbnail=fanart, plot=sinopsis, fanart=fanart, folder=False) )
    if clips:
        itemlist.append( Item(channel=CHANNELNAME, title="[COLOR red]>> Clips de vídeo[/COLOR]", action="episodios", url=url_clips, thumbnail=fanart, plot=sinopsis, fanart=fanart, folder=True) )
    return itemlist

def play(item):
    logger.info("tvalacarta.channels.dplay play")
    itemlist = []
    data = scrapertools.cache_page(item.url).replace("\n","")
    url = url_brightcove(item.url.rsplit("#")[1], data)
    itemlist.append( Item(channel=CHANNELNAME, title="", action="play", url=url, server="dplay", thumbnail=item.thumbnail, plot=item.plot, folder=False) )

    return itemlist
