# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para telemadrid
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "telemadrid"
BASE_URL = "http://www.telemadrid.es/"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.telemadrid mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Telemadrid" , url="A la carta" , action="programas", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="laOtra" , url="La Otra" , action="programas", folder=True) )

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.telemadrid programas")

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(BASE_URL)
    data = scrapertools.find_single_match(data,'<a class="dropdown-lnk" href="[^"]+" title="[^"]+">'+item.url+'</a[^<]+<ul(.*)</ul')
    
    # Extrae las zonas de los programas
    patron = '<li><a class="lnk" href="/programas/([^\/]+)/" title="[^"]+">([^<]+)</a></li>'
    matches = scrapertools.find_multiple_matches(data,patron)

    for nombre_programa,title in matches:
        url = urlparse.urljoin(BASE_URL,"/programas/"+nombre_programa+"/programas-completos/")
        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, action="episodios", show=title, folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.telemadrid episodios")

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)

    # Extrae programas destacados (solo estan en la primera pagina)
    patron  = '<img class="photo"\s+data-src="([^"]+)"[^<]+'
    patron += '<i class="media-info media-info--video"[^<]+'
    patron += '</i[^<]+'
    patron += '<a class="oop-link" href="([^"]+)"\s+'
    patron += 'title="[^"]+">([^<]+)</a[^<]+'
    patron += '</figure[^<]+'
    patron += '</div[^<]+'
    patron += '<div class="card-news__body"[^<]+'
    patron += '<time class="card__dateline" itemprop="dateline datePublished" datetime="[^"]+">([^<]+)</time>'
    matches = scrapertools.find_multiple_matches(data,patron)

    for thumbnail,scraped_url,title,scraped_aired_date in matches:
        url = urlparse.urljoin(item.url,scraped_url)
        aired_date = scrapertools.parse_date(scraped_aired_date)
        itemlist.append( Item(channel=CHANNELNAME, action="play", server="telemadrid", title=title, show=item.show, url=url, thumbnail=thumbnail, aired_date=aired_date, folder=False))

    # Extrae resto de programas
    patron  = '<img class="photo"\s+data-src="([^"]+)"[^<]+'
    patron += '<a class="oop-link" href="([^"]+)"\s+'
    patron += 'title="[^"]+">([^<]+)</a[^<]+'
    patron += '</figure[^<]+'
    patron += '</div[^<]+'
    patron += '<div class="search-item__body"[^<]+'
    patron += '<h2 class="search-item__heading"[^<]+'
    patron += '<a class="lnk" [^<]+</a></h2[^<]+'
    patron += '<time class="search-item__dateline" datetime="[^"]+">([^<]+)</time>'
    matches = scrapertools.find_multiple_matches(data,patron)

    for thumbnail,scraped_url,title,scraped_aired_date in matches:
        url = urlparse.urljoin(item.url,scraped_url)
        aired_date = scrapertools.parse_date(scraped_aired_date)
        itemlist.append( Item(channel=CHANNELNAME, action="play", server="telemadrid", title=title, show=item.show, url=url, thumbnail=thumbnail, aired_date=aired_date, folder=False))

    next_page_url = scrapertools.find_single_match(data,'<a class="pagination__navigation pagination__navigation--next" href="([^"]+)"')
    if next_page_url!="":
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page_url), action="episodios", show=item.show, folder=True) )

    return itemlist

def detalle_programa(item):
    return item

def detalle_episodio(item):

    # Ahora saca la URL
    data = scrapertools.cache_page(item.url)

    try:
        from servers import extremaduratv as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]
        item.plot = scrapertools.find_single_match(data,'<meta itemprop="description" content="(.*?)">')
        item.plot = scrapertools.decodeHtmlentities(item.plot)
        item.plot = scrapertools.htmlclean(item.plot)
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    # Comprueba que la primera opción tenga algo
    categorias_items = mainlist(Item())
    programas_items = programas(categorias_items[0])
    episodios_items = episodios(programas_items[0])

    if len(episodios_items)>0:
        return True

    return False