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
    <a href="/programas/zoom" class="ration_16-9 bg-img " style="background-image: url('https://esp.rt.com/actualidad/public_images/2015.08/original/55c0cba3c46188265e8b458a.jpg');">
    </a>
    </div>
    <p class="watches watches_bg-black">
    <span class="watches__counter" data-component="CounterEye" onclick=" return {
    publicId: '182111'
    };"></span> 
    </p>            
    <div class="summary js-programs-summary">
    <div class="summary-wrapper">
    <h3 class="header">
    <a href="/programas/zoom">
    El Zoom
    </a>                        
    </h3>
    <p>
    <a href="/programas/zoom">
    &iquest;Qu&eacute; nos pretenden ense&ntilde;ar las fotos del actual escenario internacional? &iquest;Est&aacute;n retocadas, trucadas o desenfocadas? &iquest;Qu&eacute; imagen nos quieren mostrar?...
    </a>
    </p>
    </div>
    </div>
    <span class="js-programs-info icon-i">
    i
    </span>
    </div>
    '''
    patron  = '<a href="([^"]+)" class="ration_16-9[^"]+" style="background-image: url\('
    patron += "'([^']+)'\)[^<]+"
    patron += '</a[^<]+'
    patron += '</div[^<]+'
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

def videos(item, load_all_pages=False):
    logger.info("tvalacarta.channels.rtspan videos")    
    itemlist = []

    '''
    <div class="cover">
    <a href="/programas/keiser_report/223832-eeuu-estado-puerto-rico" class="cover__media bg-img cover__media_ratio cover__image_type_video-normal"
    style="background-image: url('https://esp.rt.com/actualidad/public_images/2016.11/thumbnail/582d9f22c461884a098b45b3.jpg');">
    </a>
    </div>
    </div>
    <div class="card__heading card__heading_all-news">
    <a class="link " href="/programas/keiser_report/223832-eeuu-estado-puerto-rico">
    ¿Tendrá pronto EE. UU. un 51.º estado?
    </a></div><div class="card__date-time card__date-time_all-news"><time class="date ">
    17 noviembre 2016 | 14:19
    </time>
    '''

    data = scrapertools.cachePage(item.url)
    patron  = '<div class="cover"[^<]+'
    patron += '<a href="([^"]+)".*?'
    patron += "url\('([^']+)'.*?"
    patron += '<a class="link[^>]+>([^<]+)</a'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
	
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail
        plot = ""

        itemlist.append( Item(channel=__channel__, action="play", title=title, url=url, thumbnail=thumbnail, show=item.show, folder=False) )

    next_page_url = scrapertools.find_single_match(data,'<div class="listing__button listing__button_all-news listing__button_js" data-href="([^"]+)"')
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
