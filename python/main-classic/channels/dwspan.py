# -*- coding: utf-8 -*-
#------------------------------------------------------------------
# tvalacarta
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------------
# Canal para "Deustche Welle en español", creado por rsantaella
#------------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools
from core import jsontools

CHANNELNAME = "dwspan"
DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.dwspan mainlist")
    return programas(Item())

def programas(item):
    logger.info("tvalacarta.channels.dwspan programas")
    itemlist = []

    if item.url=="":
        item.url = "http://www.dw.com/es/tv/emisiones-tv/s-9134"

    '''
    <div class="col1 mc">
    <div class="news epg">
    <div class="teaserImg">
    <a href="/es/tv/claves/s-30468">
    <img width="220"
    height="124" border="0"
    src="/image/15682255_301.jpg"/>
    </a>
    </div>
    <div class="teaserContentWrap">
    <a href="/es/tv/claves/s-30468">
    <h2>Claves</h2>
    <p>El mundo desde América Latina</p>
    </a>
    </div>
    <ul class="smallList">
    <li>
    <strong>Actual</strong>
    <a href="/es/claves-chile-educación-sexual-inhibida/av-36127035">Claves</a>
    24.10.2016<span class="icon tv"></span> </li>
    <li>
    <a href="/es/multimedia/todos-los-contenidos/s-100838?type=18&programs=15605312">Todos los videos</a>


    <div class="col1 mc">
    <div class="news epg">
    <div class="teaserImg">
    <a href="/es/tv/life-links/s-101481">
    <img width="220"
    height="124" border="0"
    src="/image/17923250_301.png"/>
    </a>
    </div>
    <div class="teaserContentWrap">
    <a href="/es/tv/life-links/s-101481">
    <h2>Life Links</h2>
    <p>Compartir realidades. Cambiar perspectivas.</p>
    </a>
    </div>
    <ul class="smallList">
    <li>
    <strong>Actual</strong>
    <a href="/es/life-links-headabovewater-con-el-agua-al-cuello-trabajar-en-un-barco/av-35880794">Life Links</a>
    24.09.2016<span class="icon tv"></span> </li>
    <li>
    <a href="/es/multimedia/todos-los-contenidos/s-100838?type=18&programs=18365568">Todos los videos</a>
    </li>
    </ul>
    </div>
    </div>
    '''

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    #logger.info(data)


    pattern  = '<div class="col1 mc[^<]+'
    pattern += '<div class="news epg[^<]+'
    pattern += '<div class="teaserImg[^<]+'
    pattern += '<a href="([^"]+)">[^<]+'
    pattern += '<img\s+width="\d+"\s+height="\d+"\s+border="\d+"\s+src="([^"]+)"[^<]+'
    pattern += '</a[^<]+'
    pattern += '</div[^<]+'
    pattern += '<div class="teaserContentWrap"[^<]+'
    pattern += '<a[^<]+'
    pattern += '<h2>([^<]+)</h2>[^<]+'
    pattern += '<p>([^<]+)</p'
    matches = re.compile(pattern,re.DOTALL).findall(data)
    
    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot in matches:
        title = scrapedtitle
        thumbnail = urlparse.urljoin( item.url , scrapedthumbnail )
        url = urlparse.urljoin( item.url , scrapedurl.strip() )
        plot = scrapedplot

        # Appends a new item to the xbmc item list
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="episodios" , url=url, thumbnail=thumbnail, fanart=thumbnail, plot=plot , show = title, view="programs", folder=True) )

    return itemlist

def detalle_programa(item):
    logger.info("tvalacarta.channels.dwspan detalle_programa")    

    try:
        data = scrapertools.cache_page(item.url)

        item.plot = scrapertools.find_single_match(data,'<div class="col2 programClaimTeaser">.*?<p>(.*?)</div>')
        item.plot = scrapertools.htmlclean( item.plot ).strip()
    except:
        import traceback
        logger.info(traceback.format_exc())

    return item

def episodios(item):
    logger.info("tvalacarta.channels.dwspan episodios")
    itemlist = []

    # 
    '''
    <div class="col1">

    <div class="news searchres hov">
    <a href="/es/life-links-readytofight-listos-para-pelear/av-19224025">
    <div class="teaserImg tv">
    <img border="0" width="220" height="124" src="/image/18378218_301.jpg" title="Life Links - #readytofight: Listos para pelear" alt="default" /> </div>
    <h2>Life Links - #readytofight: Listos para pelear
    <span class="date">30.04.2016
    | 26:06 Minutos
    </span>
    <span class='icon tv'></span> </h2>
    <p>Un imán, un exsalafista, un ex marine de EE. UU. A todos ellos les une una meta: luchar contra el extremismo y “Estado Islámico”.</p>
    </a>
    </div>
    </div>
    '''
    if "pagenumber=" in item.url:
        data_url = item.url
    else:
        data = scrapertools.cache_page(item.url)
        # http://www.dw.com/es/multimedia/todos-los-contenidos/s-100838?type=18&programs=15535663
        # http://www.dw.com/mediafilter/research?lang=es&type=18&programs=15535663&sort=date&results=32&showteasers=true&pagenumber=1
        program_id = scrapertools.find_single_match(data,'<a href="http://www.dw.com/es/multimedia/todos-los-contenidos/s-100838.type=18&programs=([^"]+)"')
        data_url = "http://www.dw.com/mediafilter/research?lang=es&type=18&programs="+program_id+"&sort=date&results=32&showteasers=true&pagenumber=1"

    data = scrapertools.cache_page(data_url)
    pattern  = '<div class="col1"[^<]+'
    pattern += '<div class="news searchres hov"[^<]+'
    pattern += '<a href="([^"]+)"[^<]+'
    pattern += '<div class="teaserImg tv"[^<]+'
    pattern += '<img.*?src="([^"]+)"[^<]+</div>[^<]+'
    pattern += '<h2>([^<]+)'
    pattern += '<span class="date">(\d+\.\d+\.\d+)\s+\|\s+(\d+\:\d+)[^<]+'
    pattern += '</span>[^<]+'
    pattern += '<span[^<]+</span[^<]+</h2[^<]+'
    pattern += '<p>([^<]+)</p>'
    matches = re.compile(pattern,re.DOTALL).findall(data)
    logger.info( repr(matches) )

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapeddate, duration, scrapedplot in matches:
        title = scrapedtitle.strip()
        thumbnail = urlparse.urljoin( item.url , scrapedthumbnail )
        url = urlparse.urljoin( item.url , scrapedurl.strip() )
        plot = scrapedplot
        aired_date = scrapertools.parse_date(scrapeddate)

        # Appends a new item to the xbmc item list
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="play" , server="dwspan", url=url, thumbnail=thumbnail, fanart=thumbnail, plot=plot , aired_date=aired_date, duration=duration, show=item.show, view="videos", folder=False) )

    if len(itemlist)>0:
        current_page = scrapertools.find_single_match(data_url,"pagenumber=(\d+)")
        logger.info("current_page="+current_page)
        next_page = str(int(current_page)+1)
        logger.info("next_page="+next_page)
        next_page_url = data_url.replace("pagenumber="+current_page,"pagenumber="+next_page)
        logger.info("next_page_url="+next_page_url)

        itemlist.append(Item(channel=CHANNELNAME, title=">> Página siguiente" , action="episodios" , url=next_page_url, show=item.show) )


    return itemlist

def detalle_episodio(item):

    item.geolocked = "0"

    try:
        from servers import dwspan as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def play(item):

    item.server="dwspan";
    itemlist = [item]

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    items_programas = mainlist(Item())
    for item_programa in items_programas:
        items_episodios = episodios(item_programa)

        if len(items_episodios)>0:
            return True

    return False
