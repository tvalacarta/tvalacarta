# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para La Red (Chile)
# creado por rsantaella
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "laredcl"
__title__ = "laredcl"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.laredcl mainlist")

    item.url="http://lared.cl/programas"
    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.laredcl programas")    

    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    '''
    <a href="./programas/ntrevista-verdadera"><h2 class="lr-title"><b>Entrevista Verdadera</b></h2></a>
    <a href="./programas/mentiras-verdaderas"><h2 class="mv-title"><span>Mentiras</span> <b>verdaderas</b></h2></a>
    '''
    patron  = '<a href="([^"]+)"[^<]+'
    patron += '<h2 class="[^"]+">(.*?)</h2>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl,scrapedtitle in matches:
        thumbnail = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapertools.htmlclean(scrapedtitle)
        plot = ""

        itemlist.append( Item(channel=__channel__, action="episodios", title=title, show=title, url=url, thumbnail=thumbnail,  plot=plot, folder=True))

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.url)
    item.thumbnail = scrapertools.find_single_match(data,'<meta content="([^"]+)" itemprop="thumbnailUrl')

    item.plot = scrapertools.find_single_match(data,'<div class="item-text"><p class="introtext">(.*?)</div>')
    item.plot = scrapertools.htmlclean(item.plot).strip()
    
    return item

def episodios(item):
    logger.info("tvalacarta.channels.laredcl episodios")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)    
    url = scrapertools.find_single_match(data,'<h2 class="lr-title"[^<]+<span>Programas</span> <b>completos</b> <a href="([^"]+)" class="see-all">Ver todos</a></h2>')
    if url!="":
        data = scrapertools.cachePage(url)

    '''
    <div id="post-194463" class="col span_2 image-block-column" style="background-image: url('http://static.lared.cl/wp-content/uploads/2016/02/mujeres-primero-programa-complet7.jpg')" >
    <div class="item-thumbnail">
    <a href="http://lared.cl/2016/programas/mujeresprimero/programas-completos-mujeres-primero/mujeres-primero-programa-completo-martes-9-de-febrero-2016">
    <div class="overlay-thumb">
    <h3>Mujeres Primero Programa Completo Martes 9 de Febrero 2016</h3>
    </div>
    </a>
    </div>
    </div>
    '''

    patron  = '<div id="post[^"]+" class="col[^"]+" style="background-image\: '+"url\('([^']+)'\)[^<]+"
    patron += '<div class="item-thumbnail"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<div class="overlay-thumb"[^<]+'
    patron += '<h3>([^<]+)</h3>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedthumbnail,scrapedurl,scrapedtitle in matches:
        title = scrapedtitle
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""
        itemlist.append( Item(channel=__channel__, action="play", title=title, url=url, thumbnail=thumbnail, plot=plot, show=item.show, folder=False))

    next_page_url = scrapertools.find_single_match(data,'<a class="nextpostslink" rel="next" href="([^"]+)">')
    if next_page_url!="":
        itemlist.append( Item(channel=__channel__, title=">> Página siguiente" , action="episodios" , url=urlparse.urljoin(item.url,next_page_url), show=item.show) )

    return itemlist

def detalle_episodio(item):

    data = scrapertools.cache_page(item.url)

    item.plot = scrapertools.htmlclean(scrapertools.find_single_match(data,'<meta content="([^"]+)" itemprop="description')).strip()
    item.thumbnail = scrapertools.find_single_match(data,'<meta content="([^"]+)" itemprop="thumbnailUrl')

    #<meta content="miércoles, 16 de septiembre de 2015 3:30" itemprop="datePublished"
    scrapeddate = scrapertools.find_single_match(data,'<meta content="([^"]+)" itemprop="datePublished')

    item.aired_date = scrapertools.parse_date(scrapeddate)

    item.geolocked = "0"

    media_item = play(item)
    try:
        item.media_url = media_item[0].url.replace("\\","/")
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def play(item):
    logger.info("tvalacarta.channels.laredcl play")

    from servers import servertools
    return servertools.find_video_items(item)

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
