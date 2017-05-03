# -*- coding: utf-8 -*-
#------------------------------------------------------------------
# tvalacarta
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------------
# Canal para Telemundo, creado por rsantaella
#------------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core import jsontools

from core.item import Item
from servers import servertools

__channel__ = "telemundo"
__category__ = "L"
__type__ = "generic"
__title__ = "telemundo"
__language__ = "ES"
__creationdate__ = "20130322"
__vfanart__ = ""

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.telemundo mainlist")    
    itemlist = []

    '''
    <div class="grid-collection-item--MAIN">
    <a href="http://www.telemundo.com/novelas/el-fantasma-de-elena/videos" class="grid-collection-item--link">
    <span class="grid-collection-item--aspect-ratio-412x137">
    <img class="grid-collection-item--image" data-original="http://www.telemundo.com/sites/nbcutelemundo/files/styles/show_brand_grid/public/sites/nbcutelemundo/files/images/tv_show/06_ElFantasmaDeElena_596x200_2.jpg?itok=blnz-UOw" width="412" height="137" /><noscript><img class="grid-collection-item--image" src="http://www.telemundo.com/sites/nbcutelemundo/files/styles/show_brand_grid/public/sites/nbcutelemundo/files/images/tv_show/06_ElFantasmaDeElena_596x200_2.jpg?itok=blnz-UOw" width="412" height="137" /></noscript>    </span>
    <span class="grid-collection-item--name">El Fantasma de Elena</span>
    </a>
    </div>
    '''
    '''
    <div class="grid-collection-item--MAIN ">
    <a href="http://www.telemundo.com/novelas/avenida-brasil/videos" class="grid-collection-item--link">
    <span class="ratio-container-412x137">
    <img class="grid-collection-item--image" data-original="http://www.telemundo.com/sites/nbcutelemundo/files/styles/show_brand_grid/public/sites/nbcutelemundo/files/images/tv_show/06_AvenidaBrasil_596x200_2.jpg?itok=NTaAoDLf" width="1236" height="411" /><noscript><img class="grid-collection-item--image" src="http://www.telemundo.com/sites/nbcutelemundo/files/styles/show_brand_grid/public/sites/nbcutelemundo/files/images/tv_show/06_AvenidaBrasil_596x200_2.jpg?itok=NTaAoDLf" width="1236" height="411" /></noscript>    </span>
    <span class="grid-collection-item--name">Avenida Brasil</span>
    </a>
    </div>
    '''
    data = scrapertools.cachePage("http://www.telemundo.com/videos")
    patron  = '<div class="grid-collec[^<]+'
    patron += '[^0-9]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<span[^<]+'
    patron += '<img class="[^"]+"[^0-9]+data-original="([^"]+)"[^<]+'
    patron += '<noscript><img[^<]+<\/noscript[^<]+<\/span>[^<]+'
    patron += '<span class="[^"]+">([^<]+)<\/span>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        thumbnail = scrapedthumbnail
        url = scrapedurl
        programa = scrapertools.find_single_match(url,"/([^\/]+)/videos")
        url = url+"/"+programa+"/capitulos"
        itemlist.append( Item(channel=__channel__, action="episodios", title=title, url=url, thumbnail=thumbnail, show=title, view="programs", folder=True))

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.telemundo episodios")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    if "video_feed" in item.url:
        json_data = jsontools.load_json(data)
        data = json_data["slide"]
        next_page_url = json_data["nextUrl"]
    else:
        next_page_url = scrapertools.find_single_match(data,'data-feed-url-next="([^"]+)"')

    '''
    <div class="media--SHOW-BRAND-VIDEO media--active">
    <div class="media--media">
    <a href="http://www.telemundo.com/novelas/celia/videos/celia/capitulos/celia-capitulo-final-celia-muere-causa-de-un-tumor-en-el-cerebro-1046906" class="media--play-button media-item--aspect-ratio-300x215">
    <img class="media--cover-image" src="http://www.telemundo.com/sites/nbcutelemundo/files/styles/show_brand_video/public/images/mpx/2016/02/08/160208_2982200_Celia__Capitulo_Final__Celia_muere_a_causa_d.jpg?itok=DdLxQQUV" width="300" height="215" alt="Aymee Nuviola en Celia" title="Aymee Nuviola en Celia" />            </a>
    </div>
    <div class="media--content">
    <h4><a class="media--title" href="http://www.telemundo.com/novelas/celia/videos/celia/capitulos/celia-capitulo-final-celia-muere-causa-de-un-tumor-en-el-cerebro-1046906">Capítulo Final:Celia muere a causa de un tumor en el cerebro</a></h4>
    <p class="media--air-date">Emitido: lunes 02/8/16</p>
    <div class="media--description">
    <h3><a href="http://www.telemundo.com/novelas/celia/videos/celia/capitulos/celia-capitulo-final-celia-muere-causa-de-un-tumor-en-el-cerebro-1046906" class="media--link">Después de las complicaciones de salud que venia presentado, Celia parte a mejor vida dejando un legado de amor a todos los latinos en el mundo. </a></h3>
    </div>
    </div>
    </div>
    '''

    '''
    <section class="video-carousel--BRAND" data-feed-url-prev="" data-feed-url-next="http://www.telemundo.com/node/947661/video_feed?group=0&sub=0&vid=1046906&page=0%2C1">

    http://www.telemundo.com/node/947661/video_feed?group=0&sub=0&vid=1046906&page=0%2C0
    -> slide = 
    -> next_url = 
    '''

    patron  = '<div class="media--SHOW-BRAND-VIDEO[^<]+'
    patron += '<div class="media--media"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img class="media--cover-image" src="([^"]+)"[^<]+</a[^<]+'
    patron += '</div[^<]+'
    patron += '<div class="media--content"[^<]+'
    patron += '<h4><a class="media--title" href="[^"]+">([^<]+)</a></h4[^<]+'
    patron += '<p class="media--air-date">([^<]+)</p[^<]+'
    patron += '<div class="media--description"[^<]+'
    patron += '<h3><a href="[^"]+" class="media--link">([^<]+)</a></h3>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedthumbnail,scrapedtitle,aired_date,scrapedplot in matches:
        title = scrapedtitle
        url = scrapedurl
        thumbnail = scrapedthumbnail
        plot = scrapedplot
        aired_date = scrapertools.parse_date(aired_date,formato="mdy")
        itemlist.append( Item(channel=__channel__, action="partes", title=title, url=url, thumbnail=thumbnail, fanart=thumbnail, plot=plot, aired_date=aired_date, show=item.show, view="videos", folder=True))


    if next_page_url!="":
        itemlist.append( Item(channel=__channel__, title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page_url), action="episodios", show=item.show, folder=True) )


    return itemlist

def partes(item):
    #http://www.telemundo.com/novelas/2013/09/16/bella-calamidades-capitulo-1-parte-1-de-9-video-telemundo-novelas?part=0
    
    logger.info("tvalacarta.channels.telemundo partes")
    itemlist = []

    itemlist.append( Item(channel=__channel__, action="play", server="telemundo", title="Parte 1", url=item.url, folder=False))

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    #<li class="player--nav-item"><a href="http://www.telemundo.com/novelas/2013/09/16/bella-calamidades-capitulo-1-parte-1-de-9-video-telemundo-novelas?part=1" class="player--nav-number active">2</a>
    #<li class="player--nav-item"><a href="http://www.telemundo.com/novelas/2013/09/16/bella-calamidades-capitulo-1-parte-1-de-9-video-telemundo-novelas?part=1" class="player--nav-number active">2</a>    </li>
    patron = '<li class="player--nav-item"[^<]+'
    patron += '<a href="([^"]+)" class="player--nav-number active">([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    logger.info("matches="+repr(matches))

    for scrapedurl,scrapedtitle in matches:
        title = "Parte "+str(scrapedtitle)
        url = scrapedurl
        itemlist.append( Item(channel=__channel__, action="play", server="telemundo", title=title, url=url, folder=False))

    return itemlist
