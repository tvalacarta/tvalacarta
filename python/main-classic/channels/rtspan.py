# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para rtspan
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "rtspan"
__category__ = "F"
__type__ = "generic"
__title__ = "rtspan"
__language__ = "ES"
__creationdate__ = "20121212"
__vfanart__ = ""

PROGRAMAS_URL = "http://actualidad.rt.com/programas"
VIDEOS_URL = "http://actualidad.rt.com/video"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.rtspan mainlist")

    itemlist = []

    itemlist.append( Item(channel=__channel__, title="Todos los programas", action="programas", url=PROGRAMAS_URL,  fanart = __vfanart__)) 
    itemlist.append( Item(channel=__channel__, title="Últimos vídeos", action="episodios", url=VIDEOS_URL,  fanart = __vfanart__))
    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.rtspan programas")
    itemlist = []
    
    # Descarga la lista de canales
    if item.url=="":
        item.url = PROGRAMAS_URL

    data = scrapertools.cache_page(item.url)
    #logger.info("data="+data)
    '''
    <a href="/programas/keiser_report">
    <span class="ration_16-9">
    <img src="http://esp.rt.com/actualidad/public_images/2014.12/original/5485ccd571139e90488b4584.jpg" alt="Keiser report">
    </span>
    </a>
    </figure>
    <p class="watches watches_bg-black">
    <span class="watches__counter watches__counter_not-margin js-dataid" data-id="22"></span>
    </p>            
    <div class="summary js-programs-summary">
    <div class="summary-wrapper">
    <h3 class="header">
    <a href="/programas/keiser_report">
    Keiser report
    </a>                        
    </h3>
    <p>
    <a href="/programas/keiser_report">
    Keiser report &ndash; Mercados, finanzas, esc&aacute;ndalos. Keiser report es una mirada a los esc&aacute;ndalos detr&aacute;s de los titulares financieros globales.
    Sean las colusiones entre Wall...
    </a>
    '''
    patron  = '<a href="([^"]+)"[^<]+'
    patron += '<span class="ration_16-9"[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '</span[^<]+'
    patron += '</a[^<]+'
    patron += '</figure[^<]+'
    patron += '<p class="watches watches_bg-black"[^<]+'
    patron += '<span[^<]+</span[^<]+'
    patron += '</p[^<]+'
    patron += '<div class="summary js-programs-summary"[^<]+'
    patron += '<div class="summary-wrapper"[^<]+'
    patron += '<h3 class="header"[^<]+'
    patron += '<a[^>]+>([^<]+)</a[^<]+'
    patron += '</h3[^<]+'
    patron += '<p[^<]+'
    patron += '<a[^>]+>([^<]+)</a>'


    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedplot in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail
        plot = scrapertools.htmlclean(scrapedplot).strip()
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=__channel__, title=title , action="videos" , url=url, thumbnail=thumbnail, fanart=thumbnail, plot=plot , show = title , viewmode="movie_with_plot" , folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.rtspan episodios")    
    itemlist = []

    data = scrapertools.cachePage(item.url)

    patron  = '<figure class="media">.*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<img src="([^"]+)".*?'
    patron += '<time class="date">([^<]+)</time.*?'
    patron += '<h3[^<]+'
    patron += '<a[^>]+>([^<]+)</a'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
	
    for scrapedurl,scrapedthumbnail,fecha,scrapedtitle in matches:
        scrapedday = scrapertools.find_single_match(fecha,'(\d+)\.\d+\.\d+')
        scrapedmonth = scrapertools.find_single_match(fecha,'\d+\.(\d+)\.\d+')
        scrapedyear = scrapertools.find_single_match(fecha,'\d+\.\d+\.(\d+)')
        scrapeddate = scrapedyear + "-" + scrapedmonth + "-" + scrapedday

        title = fecha.strip() + " - " + scrapedtitle.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail
        itemlist.append( Item(channel=__channel__, action="play", title=title, url=url, thumbnail=thumbnail, aired_date=scrapeddate, folder=False) )

    next_page_url = scrapertools.find_single_match(data,'<button class="button-grey js-listing-more".*?data-href="([^"]+)">')
    if next_page_url!="":
        itemlist.append( Item(channel=__channel__, action="episodios", title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page_url) ,  folder=True) )    

    return itemlist

def detalle_episodio(item):

    data = scrapertools.cache_page(item.url)

    item.plot = scrapertools.htmlclean(scrapertools.find_single_match(data,'<meta property="og:description" content="([^"]+)"')).strip()
    item.thumbnail = scrapertools.find_single_match(data,'<meta property="og:image" content="([^"]+)"')
    item.geolocked = "0"
    item.aired_date = scrapertools.find_single_match(data,'<meta name="publish-date" content="([^\s]+)')

    media_item = play(item)
    try:
        item.media_url = media_item[0].url
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def videos(item, load_all_pages=True):
    logger.info("tvalacarta.channels.rtspan videos")    
    itemlist = []

    data = scrapertools.cachePage(item.url)
    '''
    <a href="/programas/la_lista_de_erick/182394-lista-erick-revancha-tierra-osos-rusia">
    <span class="ration_16-9">
    <img src="http://esp.rt.com/actualidad/public_images/2015.08/thumbnail/55c4c67dc46188c01c8b462b.jpg" alt="lista de erick">
    <i class="icond-video">
    <span class="play">
    &nbsp;
    </span>
    </i>
    </span>
    </a>
    </figure>
    <time class="date">
    07.08.2015
    </time>
    <span class="watches">
    <span class="watches__counter js-dataid" data-id="182394"></span>
    </span>
    <h3>
    <a href="/programas/la_lista_de_erick/182394-lista-erick-revancha-tierra-osos-rusia">La lista de Erick: La revancha en tierra de osos</a>
    </h3>
    '''
    patron  = '<a href="([^"]+)"[^<]+'
    patron += '<span class="ration_16-9"[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '<i class="icond-video"[^<]+'
    patron += '<span class="play"[^<]+'
    patron += '</span[^<]+'
    patron += '</i[^<]+'
    patron += '</span[^<]+'
    patron += '</a[^<]+'
    patron += '</figure[^<]+'
    patron += '<time class="date">([^<]+)</time[^<]+'
    patron += '<span class="watches"[^<]+'
    patron += '<span[^<]+</span[^<]+'
    patron += '</span[^<]+'
    patron += '<h3[^<]+'
    patron += '<a[^>]+>([^<]+)</a>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
	
    for scrapedurl,scrapedthumbnail,fecha,scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail
        plot = ""

        scrapedday = scrapertools.find_single_match(fecha,'(\d+)\.\d+\.\d+')
        scrapedmonth = scrapertools.find_single_match(fecha,'\d+\.(\d+)\.\d+')
        scrapedyear = scrapertools.find_single_match(fecha,'\d+\.\d+\.(\d+)')
        scrapeddate = scrapedyear + "-" + scrapedmonth + "-" + scrapedday

        itemlist.append( Item(channel=__channel__, action="play", title=title, url=url, thumbnail=thumbnail, show=item.show, aired_date=scrapeddate, folder=False) )

    next_page_url = scrapertools.find_single_match(data,'<button class="button-grey js-listing-more" style="[^"]+" data-href="([^"]+)">')
    if next_page_url!="":
        next_page_item = Item(channel=__channel__, action="videos", title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page_url) , show=item.show, folder=True)

        if load_all_pages:
            itemlist.extend(videos(next_page_item,load_all_pages))
        else:
            itemlist.append(next_page_item)


    return itemlist

def play(item):
    logger.info("tvalacarta.channels.rtspan play")    
    itemlist = []

    data = scrapertools.cachePage(item.url)

    video_url = scrapertools.find_single_match(data,'www.youtube.com/embed/([^"]+)"')
    if video_url!="":
        itemlist.append( Item(channel=__channel__, action="play", server="youtube", title=item.title , url="http://www.youtube.com/watch?v="+video_url ,  folder=False) )
    else:
        video_url = scrapertools.find_single_match(data,'href="([^"]+)">Descargar video</a>')
        if video_url!="":
            itemlist.append( Item(channel=__channel__, action="play", server="directo", title=item.title , url=video_url ,  folder=False) )
        else:
            video_url = scrapertools.find_single_match(data,'file\:\s+"([^"]+)"')
            itemlist.append( Item(channel=__channel__, action="play", server="directo", title=item.title , url=video_url ,  folder=False) )

    return itemlist

def test():

    # Al entrar sale una lista de programas
    programas_items = mainlist(Item())
    if len(programas_items)==0:
        print "No devuelve programas"
        return False

    videos_items = videos(programas_items[0])
    if len(videos_items)==1:
        print "No devuelve videos en "+programas_items[0].title
        return False

    return True
