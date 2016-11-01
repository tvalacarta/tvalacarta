# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para rtvcm
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import scrapertools
from core.item import Item
from core import jsontools

DEBUG = False
__channel__ = "rtvcm"
MAIN_URL = "http://www.cmmedia.es/wp-json/web/v1/programas/tv/alphab/null"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.rtvcm.mainlist")
    return programas(item)

def programas(item):
    logger.info("tvalacarta.rtvcm.programas")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(MAIN_URL)

    '''
    <li class="col-sm-6 col-md-4">
    <article>
    <figure>
    <img src="http://www.cmmedia.es/television/wp-content/uploads/2016/10/A-los-ojos_miniatura
    .jpg" alt="A los ojos">
    <a class="" href="http://www.cmmedia.es/programas/tv/a-los-ojos" title="A los ojos"
    ><span class="sr-only">A los ojos</span></a>
    </figure>
    <h3><a href="http://www.cmmedia.es/programas/tv/a-los-ojos" title="A
    los ojos">A los ojos</a></h3>
    <p>Cine</p>
    </article>
    </li>


    <li class="col-sm-6 col-md-4">
    <article>
    <figure>
    <img src="http://www.cmmedia.es/television/wp-content/uploads/2015/03/ATV16_MINIATURA-FICHA-copia
    .png" alt="A tu vera">
    <a class="icon-play-circle" href="http://www.cmmedia.es/programas/tv/a-tu-vera" title
    ="A tu vera"><span class="sr-only">A tu vera</span></a>
    </figure>
    <h3><a href="http://www.cmmedia.es/programas/tv/a-tu-vera" title="A tu
    vera">A tu vera</a></h3>
    <p>Entretenimiento</p>
    </article>
    </li>
    '''

    patron  = '<li class="col[^<]+'
    patron += '<article[^<]+'
    patron += '<figure[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '<a class="icon-play-circle" href="([^"]+)"[^<]+'
    patron += '<span class="sr-only">([^<]+)</span></a>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedthumbnail,scrapedurl,scrapedtitle in matches:
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)+"/videos"
        title = scrapedtitle
        plot = ""

        itemlist.append( Item(channel=__channel__, action="episodios", title=title, show=title, url=url, thumbnail=thumbnail,  plot=plot, view="videos", folder=True))

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.url)

    item.plot = scrapertools.find_single_match(data,'<meta property="og:description" content="([^"]+)"')

    return item

def episodios(item):
    logger.info("tvalacarta.rtvcm.episodios")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    '''
    <article>
    <figure>
    <img src="http://api.rtvcm.webtv.flumotion.com/videos/31351/poster.jpg?w=7fe8fa22" alt="Cosecha propia">
    <a class="icon-play-circle" href="http://www.cmmedia.es/programas/tv/cosecha-propia/videos/31351" title="Cosecha propia"><span class="sr-only">http://api.rtvcm.webtv.flumotion.com/videos/31351/poster.jpg?w=7fe8fa22</span></a>
    </figure>
    <p class="date"><time>24/09/2016</time></p>
    <h3><a href="http://www.cmmedia.es/programas/tv/cosecha-propia/videos/31351" title="Cosecha propia">Cosecha propia</a></h3>
    <p>Venta de Don Quijote</p>
    </article>
    '''

    patron  = '<article[^<]+'
    patron += '<figure[^<]+'
    patron += '<img src="([^"]+)" alt="([^"]+)"[^<]+'
    patron += '<a class="icon-play-circle" href="([^"]+)"[^<]+<span[^<]+</span></a[^<]+'
    patron += '</figure[^<]+'
    patron += '<p class="date"><time>([^<]+)</time></p[^<]+'
    patron += '<h3><a[^<]+</a></h3[^<]+'
    patron += '<p>([^<]+)</p>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedthumbnail,scrapedtitle,scrapedurl,fecha,scrapedplot in matches:
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapedtitle+" "+fecha
        plot = scrapedplot
        aired_date = scrapertools.parse_date(fecha)

        itemlist.append( Item(channel=__channel__, title=title , url=url, plot=plot, thumbnail=thumbnail , fanart=thumbnail , action="play" , server="rtvcm", show = item.title , aired_date=aired_date, folder=False) )

    next_page_url = scrapertools.find_single_match(data,'<a href="([^"]+)" aria-label="Siguiente">')
    if next_page_url!="":
        itemlist.append( Item(channel=__channel__, action="episodios", title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page_url) ,  folder=True) )    

    return itemlist

def detalle_episodio(item):
    logger.info("tvalacarta.rtvcm.detalle_episodio")

    data = scrapertools.cache_page(item.url)

    try:
        json_object = jsontools.load_json(data)

        item.geolocked = "0"
        item.aired_date = scrapertools.parse_date(item.title)

        from servers import rtvcm as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]

    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def play(item):

    item.server="rtvcm"
    itemlist = [item]

    return itemlist    

def test():

    # Al entrar sale una lista de categorias
    categorias_items = mainlist(Item())
    if len(categorias_items)==0:
        print "No devuelve categorias"
        return False

    programas_items = programas(categorias_items[0])
    if len(programas_items)==0:
        print "No devuelve programas en "+categorias_items[0]
        return False

    episodios_items = episodios(programas_items[0])
    if len(episodios_items)==0:
        print "No devuelve videos en "+programas_items[0].title
        return False

    return True