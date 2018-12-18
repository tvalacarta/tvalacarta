# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para sietetvandalucia
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "sietetvandalucia"

def mainlist(item):
    logger.info("tvalacarta.channels.sietetvandalucia mainlist")

    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.sietetvandalucia programas")

    # Descarga la página de uno de los programas, porque hay un combo de programas y es más ligera que la portada
    item = Item(url="https://7tvandalucia.es/andalucia/puerta-grande/7/")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data,'<ul class="dropdown"(.*?)</ul>')

    # Parse
    patron  = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = scrapertools.find_multiple_matches(data,patron)

    for scraped_url,title in matches:
        url = urlparse.urljoin(item.url,scraped_url)

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, action="episodios", show=title, folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.sietetvandalucia episodios")

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)

    # Parse
    '''
    <div class="wrap-toggle active">
    <div>
    <input type="checkbox" id="question0" name="q"  class="questions">
    <div class="plus">+</div>
    <label for="question0" class="question">
    Listado de episodios de la temporada 5                            </label>
    <div class="answers">
    <ul>
    <li><a href="https://7tvandalucia.es/andalucia/cuaderno-agrario/5-14-08122018-cuaderno-agrario/43608/" > Número 14 / 08/12/2018 Cuaderno Agrario</a></li>
    <li><a href="https://7tvandalucia.es/andalucia/cuaderno-agrario/5-13-01122018-cuaderno-agrario/43508/" > Número 13 / 01/12/2018 Cuaderno Agrario</a></li>
    ...
    </ul>
    '''
    patron  = '<div class="wrap-toggle active"[^<]+'
    patron += '<div[^<]+'
    patron += '<input type="checkbox"[^<]+'
    patron += '<div class="plus"[^<]+</div[^<]+'
    patron += '<label[^>]+>([^<]+)</label[^<]+'
    patron += '<div class="answers"[^<]+'
    patron += '<ul(.*?)</ul'

    matches = scrapertools.find_multiple_matches(data,patron)
    for season_title,season_body in matches:

        season_label = season_title.strip()
        season_label = season_label.replace("Listado de episodios de la ","").capitalize()

        patron = '<li><a href="([^"]+)[^>]+>([^<]+)</a>'
        matches2 = scrapertools.find_multiple_matches(season_body,patron)

        for scraped_url,scraped_title in matches2:
            url = urlparse.urljoin(item.url,scraped_url)
            title = season_label + " " + scraped_title.strip()
            aired_date = scrapertools.parse_date(title)
            itemlist.append( Item(channel=CHANNELNAME, action="play", server="sietetvandalucia", title=title, show=item.show, url=url, aired_date=aired_date, folder=False))

    return itemlist
