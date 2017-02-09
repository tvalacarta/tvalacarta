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

    patron  = '<li class="col[^<]+'
    patron += '<article[^<]+'
    patron += '<figure[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '<a class="[^"]*" href="([^"]+)" title="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedthumbnail,scrapedurl,scrapedtitle in matches:
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        #http://www.cmmedia.es/programas/tv/a-tu-vera/programas-completos/
        url = urlparse.urljoin(item.url,scrapedurl)
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
    prueba_urls = []
    if "?pagina=" in item.url:
        prueba_urls.append(item.url)
    else:
        prueba_urls.append(item.url+"/programas-completos")
        prueba_urls.append(item.url+"/videos")
    
    for prueba_url in prueba_urls:
        data = scrapertools.cache_page(prueba_url)
        logger.info("tvalacarta.rtvcm.episodios data="+data)

        '''
        <article>
        <figure>
        <img src="http://api.rtvcm.webtv.flumotion.com/videos/30531/poster.jpg?w=f720f390" alt="Promo A tu vera Mini">
        <a class="icon-play-circle" href="http://www.cmmedia.es/programas/tv/a-tu-vera//programas-completos/30531?pagina=2" title="Promo A tu vera Mini">
        <span class="sr-only">http://api.rtvcm.webtv.flumotion.com/videos/30531/poster.jpg?w=f720f390</span></a>
        </figure>
        <p class="date"><time></time></p>
        <h3><a href="http://www.cmmedia.es/programas/tv/a-tu-vera//programas-completos/30531?pagina=2" title="Promo A tu vera Mini">Promo A tu vera Mini</a></h3>
        <p>La novena edición de A Tu Vera Mini ya está en marcha. Participa en los casting llamando al 905 447 366</p>
        </article>
        '''

        patron  = '<article[^<]+'
        patron += '<figure[^<]+'
        patron += '<img src="([^"]+)" alt="([^"]+)"[^<]+'
        patron += '<a class="icon-play-circle" href="([^"]+)"[^<]+'
        patron += '<span[^<]+</span></a[^<]+'
        patron += '</figure[^<]+'
        patron += '<p class="date"><time>([^<]*)</time></p[^<]+'
        patron += '<h3><a[^<]+</a></h3[^<]+'
        patron += '<p>(.*?)</p>'

        matches = re.compile(patron,re.DOTALL).findall(data)

        for scrapedthumbnail,scrapedtitle,scrapedurl,fecha,scrapedplot in matches:
            thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
            url = urlparse.urljoin(item.url,scrapedurl)
            title = scrapedtitle+" "+fecha
            plot = scrapedplot
            aired_date = scrapertools.parse_date(fecha)

            itemlist.append( Item(channel=__channel__, title=title , url=url, plot=plot, thumbnail=thumbnail , fanart=thumbnail , action="play" , server="rtvcm", show = item.title , aired_date=aired_date, folder=False) )

        if len(itemlist)>0:
            break

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