# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Ecuador TV
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "ecuadortv"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.ecuadortv mainlist")

    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.ecuadortv canal")

    item.url = "http://www.ecuadortv.ec/television"

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    
    '''
    <div class="field field-name-field-icon field-type-image field-label-hidden">
    <div class="field-items">
    <div class="field-item even">
    <a href="/programas/al-medios-dia">
    <img typeof="foaf:Image" src="http://www.ecuadortv.ec/sites/default/files/styles/program_menu_item/public/program/almediodiaweb_0.png?itok=wv9Isyhi" width="155" height="105" alt="" />
    </a>
    </div>
    </div>
    </div>
    <div class="field field-name-title field-type-ds field-label-hidden">
    <div class="field-items">
    <div class="field-item even" property="dc:title"
    ><h2>Al Medio Día </h2></div></div></div></div>
    '''

    # Extrae las zonas de los programas
    patron  = '<div class="field-item even"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img typeof="foaf.Image" src="([^"]+)".*?'
    patron += '<h2>([^<]+)</h2>'


    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail
        plot = ""

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="episodios", show=title, folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.ecuadortv episodios")

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)

    '''
    <div class="item-thumbnail">
    <div class="field field-name-rtv-video-thumb field-type-ds field-label-hidden">
    <div class="field-items">
    <div class="field-item even">
    <a href="/rtv/streaming/vod/46056" class="play-trigger use-ajax" data-video-id="FTb5jhfjJ-Y">
    <span class="img">
    <img src="http://img.youtube.com/vi/FTb5jhfjJ-Y/mqdefault.jpg" alt="" width="278" height="190" />
    </span>
    <span class="play-button play_big"> </span></a></div></div></div>  </div>
    <div class="slider_caption display_none">
    <div class="field field-name-title field-type-ds field-label-hidden">
    <div class="field-items">
    <div class="field-item even" property="dc:title">
    <h2>Palabra Amazónica - cap. 08
    </h2>
    </div>
    </div>
    </div>
    <div class="field field-name-field-chapter field-type-taxonomy-term-reference field-label-above">
    <div class="field-label">Capítulo:&nbsp;
    </div>
    <div class="field-items"><div class="field-item even"><span class="lineage-item lineage-item-level-0">8</span></div></div></div>  </div>    
    '''

    '''
    <div class="slider_caption display_none">
    <div class="field field-name-title field-type-ds field-label-hidden">
    <div class="field-items">
    <div class="field-item even" property="dc:title">
    <h2>Ecuador Multicolor
    </h2>
    </div>
    </div>
    </div>
    <div class="field field-name-rtv-description field-type-ds field-label-hidden">
    <div class="field-items">
    <div class="field-item even">
    <p>
    <span style="font-size:16px;">Cantón Pillaro - II parte</span></p>
    '''

    # Extrae las zonas de los videos
    patron  = '<div class="item-thumbnail"[^<]+'
    patron += '<div class="field[^<]+'
    patron += '<div class="field[^<]+'
    patron += '<div class="field[^<]+'
    patron += '<a href="[^"]+" class="[^"]+" data-video-id="([^"]+)"[^<]+'
    patron += '<span class="img"[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '</span[^<]+'
    patron += '<span[^<]+</span[^<]+</a[^<]+</div[^<]+</div[^<]+</div[^<]+</div[^<]+'
    patron += '<div class="slider_caption[^<]+'
    patron += '<div class="field[^<]+'
    patron += '<div class="field[^<]+'
    patron += '<div class="field[^<]+'
    patron += '<h2>([^<]+)</h2'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for youtube_id,scrapedthumbnail,scrapedtitle in matches:
        title = scrapedtitle
        url = "https://www.youtube.com/watch?v="+youtube_id
        thumbnail = scrapedthumbnail
        plot = ""

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