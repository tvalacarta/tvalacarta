# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para TV Pública (Argentina)
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "tvpublica"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.tvpublica mainlist")

    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.tvpublica canal")

    item.url = "http://www.tvpublica.com.ar/programas/"

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    
    '''
    <li itemscope itemtype="http://schema.org/CreativeWork" data-id="id-28" class="clearfix portfolio-item col-sm-2 masonry-item masonry-gallery-item  educacion ">
    <figure class="animated-overlay overlay-alt">
    <img itemprop="image" src="http://www.tvpublica.com.ar/wp-content/uploads/resources/escarapela-y-tvp.gif" loop="infinite" alt="Los 7 locos" data-echo="http://www.tvpublica.com.ar/wp-content/uploads/2014/07/los-7-locos-420x315.jpg" />
    <a href="http://www.tvpublica.com.ar/programa/los-7-locos/" class="link-to-post"></a><figcaption><div class="thumb-info thumb-info-alt"><i class="ss-navigateright"></i></div></figcaption></figure>
    <div class="portfolio-item-details" style="text-align:center;padding:0px 10px 0px 10px;height:84px" >
    <h3 class="portfolio-item-title" style="text-align:center;vertical-align:middle;display: table-cell;width:inherit;height:inherit;font-size:14px;line-height:20px" itemprop="name headline"><a href="http://www.tvpublica.com.ar/programa/los-7-locos/" class="link-to-post">Los 7 locos</a></h3>
    </div>
    </li>
    '''

    # Extrae las zonas de los programas
    patron  = '<li itemscop[^<]+'
    patron += '<figure[^<]+'
    patron += '<img itemprop="[^"]+" src="[^"]+" loop="[^"]+" alt="([^"]+)" data-echo="([^"]+)"[^<]+'
    patron += '<a href="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedtitle,scrapedthumbnail,scrapedurl in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail
        plot = ""

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="episodios", show=title, folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.tvpublica episodios")

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)

    '''
    div class="spb_content_element columnas-4 spb_text_column articulo">
    <div class="spb_wrapper clearfix video-modal">
    <div class="media-wrapper proporcion16-9 play" data-youtubeids="[&quot;cIcAXwUBT6o&quot;,&quot;xL8GtCV3yPE&quot;,&quot;lCh_y71jlEk&quot;,&quot;ex3NyTwJu-0&quot;]">
    <img
    id="vid-82454"
    class="video-container"
    data-echo="http://cdnsp.tvpublica.com.ar/wp-content/uploads/2017/04/15121703/educaci%C3%B3n-siglo-xxi.jpg"
    src="">
    </div>
    <a href="http://www.tvpublica.com.ar/articulo/que-escuela-se-necesita-en-el-siglo-xxi/">
    <small>Caminos de tiza</small>  <h3>¿Qué escuela se necesita en el Siglo XXI?</h3>
    <p>Mirta Goldberg junto a un grupo de especialistas nos invitan a pensar si en estos tiempos modernos, es necesario modificar los contenidos y metodología de enseñanza.</p>
    </a>
    </div>
    </div>
    '''

    # Extrae las zonas de los videos
    patron  = 'div class="spb_content_element[^<]+'
    patron += '<div class="spb_wrapper[^<]+'
    patron += '<div class="media-wrapper[^<]+'
    patron += '<img\s+id="[^"]+"\s+class="video-container"\s+data-echo="([^"]+)"\s+src=""[^<]+'
    patron += '</div[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<small>[^<]+</small[^<]+'
    patron += '<h3>([^<]+)</h3[^<]+'
    patron += '<p>([^<]+)</p>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedthumbnail,scrapedurl,scrapedtitle,scrapedplot in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail
        plot = scrapedplot

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="partes", show=item.show, folder=True) )

    next_page_url = scrapertools.find_single_match(data,'<ul class="pager pager-load-more"><li class="pager-next first last"><a href="([^"]+)">Ver m')
    if next_page_url!="":
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page_url), action="episodios", show=item.show, folder=True) )

    return itemlist

def partes(item):
    logger.info("tvalacarta.channels.tvpublica partes")

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)

    '''
    <iframe width="100%" height="100%" src="http://www.youtube.com/embed?listType=playlist&playlist=cIcAXwUBT6o,xL8GtCV3yPE,lCh_y71jlEk,ex3NyTwJu-0" frameborder="0" allowfullscreen>
    '''

    iframe = scrapertools.find_single_match(data,'<iframe width="[^"]+" height="[^"]+" src="([^"]+)"')
    ids = scrapertools.find_single_match(iframe,'playlist=(.*?)$')

    patron = "[a-zA-Z0-9_-]+"
    matches = re.compile(patron,re.DOTALL).findall(ids)

    i=1
    for youtube_id in matches:
        title = "Parte "+str(i)
        url = "https://www.youtube.com/watch?v="+youtube_id
        thumbnail = ""
        plot = ""
        i=i+1

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="play", server="youtube", show=item.show, folder=False) )

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