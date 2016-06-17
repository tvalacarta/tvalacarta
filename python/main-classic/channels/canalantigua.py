# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para Canal Antigua (Guatemala)
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

__channel__ = "canalantigua"
__title__ = "canalantigua"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.canalantigua mainlist")

    item.url="https://canalantigua.tv/programas/"
    item.view="programs"
    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.canalantigua programas")    

    itemlist = []
    # Descarga la página
    data = scrapertools.cachePage(item.url)
    '''
    <figure class="wpb_wrapper vc_figure">
    <a href="https://canalantigua.tv/programas/a-las-845-p-m" target="_self" class="vc_single_image-wrapper   vc_box_border_grey"><img class="vc_single_image-img " src="https://canalantigua.tv/wp-content/uploads/2014/02/banner-1024x800-a-las-845pm-01-320x250.jpg" width="320" height="250" alt="banner 1024x800 a las 845pm-01" title="banner 1024x800 a las 845pm-01" /></a>
    </figure>
    '''
    patron  = '<figure class="wpb_wrapper vc_figure"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img class="vc_single_image-img " src="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl,scrapedthumbnail in matches:
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)

        scrapedtitle = scrapedurl
        if scrapedtitle.endswith("/"):
            scrapedtitle = scrapedtitle[0:-1]
        title = scrapedtitle.split("/")[-1]
        title = title.replace("-"," ").capitalize()
        plot = ""

        itemlist.append( Item(channel=__channel__, action="episodios", title=title, show=title, url=url, thumbnail=thumbnail,  fanart=thumbnail,  plot=plot, view="videos", folder=True))

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.url)
    item.thumbnail = scrapertools.find_single_match(data,'<meta content="([^"]+)" itemprop="thumbnailUrl')

    item.plot = scrapertools.find_single_match(data,'<div class="item-text"><p class="introtext">(.*?)</div>')
    item.plot = scrapertools.htmlclean(item.plot).strip()
    
    return item

def episodios(item):
    logger.info("tvalacarta.channels.canalantigua episodios")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    '''
    <div class="td_module_1 td_module_wrap td-animation-stack" itemscope itemtype="https://schema.org/Article">
    <div class="td-module-image">
    <div class="td-module-thumb"><a href="https://canalantigua.tv/de-los-20-a-los-50-octubre-mes-de-la-lucha-contra-el-cancer-programa-completo/" rel="bookmark" title="De los 20 a los 50 &#8211; Octubre, mes de la lucha contra el cáncer (Programa Completo)"><img width="324" height="160" itemprop="image" class="entry-thumb" src="https://canalantigua.tv/wp-content/uploads/2015/10/211-324x160.png" alt="" title="De los 20 a los 50 &#8211; Octubre, mes de la lucha contra el cáncer (Programa Completo)"/><span class="td-video-play-ico"><img width="40" class="td-retina" src="https://canalantigua.tv/wp-content/themes/Newspaper/images/icons/ico-video-large.png" alt="video"/></span></a></div>                            </div>
    <h3 itemprop="name" class="entry-title td-module-title"><a itemprop="url" href="https://canalantigua.tv/de-los-20-a-los-50-octubre-mes-de-la-lucha-contra-el-cancer-programa-completo/" rel="bookmark" title="De los 20 a los 50 &#8211; Octubre, mes de la lucha contra el cáncer (Programa Completo)">De los 20 a los 50 &#8211; Octubre, mes de la...</a></h3>
    <div class="td-module-meta-info">
    <div class="td-post-date"><time  itemprop="dateCreated" class="entry-date updated td-module-date" datetime="2015-10-21T14:52:50+00:00" >21/10/2015</time><meta itemprop="interactionCount" content="UserComments:0"/></div>                            </div>
    <meta itemprop="author" content = "canalantigua_admin"><meta itemprop="datePublished" content="2015-10-21T14:52:50+00:00"><meta itemprop="headline " content="De los 20 a los 50 - Octubre, mes de la lucha contra el cáncer (Programa Completo)"><meta itemprop="image" content="https://canalantigua.tv/wp-content/uploads/2015/10/211.png"><meta itemprop="interactionCount" content="UserComments:0"/>        </div>
    '''
    patron  = 'itemtype="https://schema.org/Article"[^<]+'
    patron += '<div class="td-module-image"[^<]+'
    patron += '<div class="td-module-thumb"[^<]+'
    patron += '<a href="([^"]+)" rel="bookmark" title="([^"]+)"[^<]+'
    patron += '<img.*?src="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""
        itemlist.append( Item(channel=__channel__, action="play", title=title, url=url, thumbnail=thumbnail, plot=plot, show=item.show, folder=False))
    
    
    next_page_url = scrapertools.find_single_match(data,'<a href="([^"]+)"[^<]+<i class="td-icon-menu-right"></i></a>')
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
    logger.info("tvalacarta.channels.canalantigua play")

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
