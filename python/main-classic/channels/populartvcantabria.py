# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para populartvcantabria
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "populartvcantabria"

def mainlist(item):
    logger.info("tvalacarta.channels.populartvcantabria mainlist")

    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.populartvcantabria programas")

    # Descarga la página de uno de los programas, porque hay un combo de programas y es más ligera que la portada
    item = Item(url="https://populartvcantabria.com/")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data,'<a href="[^"]+">TV A LA CARTA(.*?)<a href=".">OPINI')

    # Parse
    patron  = '<li id="[^"]+" class="menu-item menu-item-type-taxonomy menu-item-object-category menu-item-\d+"><a href="([^"]+)">([^<]+)</a></li>'
    matches = scrapertools.find_multiple_matches(data,patron)

    for scraped_url,title in matches:
        url = urlparse.urljoin(item.url,scraped_url)

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, action="episodios", show=title, folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.populartvcantabria episodios")

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)

    # Parse
    '''
    <div class="td-module-thumb">
    <a href="https://populartvcantabria.com/2018/10/09/mejorando-cantabria-septiembre-2018/" rel="bookmark" class="td-image-wrap" title="Mejorando Cantabria septiembre 2018">
    <img width="534" height="462" class="entry-thumb" src="https://populartvcantabria.com/wp-content/uploads/2018/10/posttypevideop71842-youtube-thumbnail-534x462.jpg" alt="" title="Mejorando Cantabria septiembre 2018"/>
    '''
    patron  = '<div class="td-module-thumb"[^<]+'
    patron += '<a href="([^"]+)" rel="bookmark" class="td-image-wrap" title="([^"]+)"[^<]+'
    patron += '<img width="\d+" height="\d+" class="entry-thumb" src="([^"]+)"'

    matches = scrapertools.find_multiple_matches(data,patron)

    if item.title==">> Página siguiente":
        matches = matches[5:-1]

    for scraped_url,scraped_title,thumbnail in matches:
        url = urlparse.urljoin(item.url,scraped_url)
        title = scraped_title.strip()
        itemlist.append( Item(channel=CHANNELNAME, action="play", server="populartvcantabria", title=title, show=item.show, thumbnail=thumbnail, url=url, folder=False))

    next_page_url = scrapertools.find_single_match(data,'<a href="([^"]+)"[^<]+<i class="td-icon-menu-right"></i></a><span class="pages">')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , url=next_page_url, action="episodios", show=item.show, folder=True) )

    return itemlist
