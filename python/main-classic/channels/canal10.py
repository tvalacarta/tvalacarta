# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Canal 10 (Uruguay)
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "canal10"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.canal10 mainlist")

    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.canal10 canal")

    item.url = "http://www.canal10.com.uy/widgets/minisites?type=all"

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    
    '''
    <li class='minisite'>
    <a href='/uruguayos-en-el-mundo'>
    <div>
    <img alt='Uruguayos en el mundo' src='//web10.images.production.s3.amazonaws.com/uploads/minisite/mini_banner/119/Uruguayos_en_el_Mundo.jpg'>
    <p>Uruguayos en el mundo</p>
    </div>
    </a>
    </li>
    '''

    # Extrae las zonas de los programas
    patron  = "<li class='minisite'[^<]+"
    patron += "<a href='([^']+)'[^<]+"
    patron += "<div[^<]+"
    patron += "<img alt='([^']+)' src='([^']+)'"

    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        title = scrapedtitle

        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = "http:"+scrapedthumbnail
        plot = ""

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="episodios", show=title, folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.canal10 episodios")

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)

    if not "widgets/playlists" in item.url:
        #http://www.canal10.com.uy/widgets/playlists/189?per_page=6
        #         <div id='ictag_liquid/playlist_tag' class='widget' data-href='/widgets/playlists/189' data-stream='per_page=6'></div>
        playlist = scrapertools.find_single_match(data,"<div id='ictag_liquid/playlist_tag' class='widget' data-href='([^']+)' data-stream='[^']+'")
        pagination = scrapertools.find_single_match(data,"<div id='ictag_liquid/playlist_tag' class='widget' data-href='[^']+' data-stream='([^']+)'")
        url = "http://www.canal10.com.uy"+playlist+"?"+pagination

        data = scrapertools.cache_page(url)

    '''
    <li class='video'>
    <article class='video'>
    <h1 class='title'>
    <a href="http://www.canal10.com.uy/uruguayos-en-el-mundo/2016/uruguayos-en-el-mundo-por-copenhague-parte-2" class="main-link" data-stream="/widgets/videos/uruguayos-en-el-mundo-por-copenhague-parte-2/embed">Uruguayos en el mundo por Copenhague - Parte 2</a>
    </h1>
    <a class='main-link' data-stream='/widgets/videos/uruguayos-en-el-mundo-por-copenhague-parte-2/embed' href='http://www.canal10.com.uy/uruguayos-en-el-mundo/2016/uruguayos-en-el-mundo-por-copenhague-parte-2'>
    <div class='thumb'>
    <div class='play-button'></div>
    <img alt="Uruguayos en el mundo por Copenhague - Parte 2" src="//web10.images.production.s3.amazonaws.com/uploads/video/custom_thumbnail/28655/uruguayos2PIC.jpg" />
    </div>
    <h1 class='title-video' style='display:none;'>
    Uruguayos en el mundo por Copenhague - Parte 2
    </h1>
    <div class='info' style='display:none'>
    <p class='playlist'>Uruguayos en el mundo 2016</p>
    <p class='duration'>00:00:00</p>
    </div>
    <p class='description'>Imperdible edición de Uruguayos en el mundo por la ciudad de Copenhague, con la conducción de Aureliano Folle. Bloque 2. 21-10-16.</p>
    <a href='http://www.canal10.com.uy/uruguayos-en-el-mundo/2016/uruguayos-en-el-mundo-por-copenhague-parte-2' class='video-more'>ver mas</a>
    </a>
    <ul class='tags'></ul>
    </article>

    </li>
    '''

    patron = "<article class='video'>(.*?)</article>"
    matches = re.compile(patron,re.DOTALL).findall(data)

    for bloque in matches:
        title = scrapertools.find_single_match(bloque,'<img alt="([^"]+)" src="[^"]+"')
        url = scrapertools.find_single_match(bloque,'<a href="([^"]+)"')
        thumbnail = scrapertools.find_single_match(bloque,'<img alt="[^"]+" src="([^"]+)"')
        plot = scrapertools.find_single_match(bloque,"<p class='description'>([^<]+)</p>")

        # URL absoluta
        thumbnail = "http:"+thumbnail

        if title!="":
            itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="play", server="canal10", show=item.show, folder=False) )

    next_page_url = scrapertools.find_single_match(data,'<span class="next"[^<]+<a href="([^"]+)" rel="next">Sig')
    if next_page_url!="":
        next_page_url = "http://www.canal10.com.uy/"+next_page_url.replace("&amp;","&")
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page_url), action="episodios", show=item.show, folder=True) )

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    # Comprueba que la primera opción tenga algo
    categorias_items = mainlist(Item())
    programas_items = programas(categorias_items[0])
    episodios_items = episodios(programas_items[0])

    if len(episodios_items)>0:
        return True

    return False