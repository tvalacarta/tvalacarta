# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Monte Carlo (Uruguay)
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import logger
from core import scrapertools
from core import config
from core.item import Item

DEBUG = config.get_setting("debug")
CHANNELNAME = "montecarlo"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.montecarlo mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Programas"      , action="programas"    , url="http://www.montecarlotv.com.uy/programas") )
    itemlist.append( Item(channel=CHANNELNAME, title="Videoteca"      , action="programas"    , url="http://www.montecarlotv.com.uy/videoteca") )

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.montecarlo programas")
    itemlist = []

    # Descarga la página
    '''
    <div class="col-lg-4 col-md-4 col-sm-6 col-xs-12">
    <div class="div_programas_contenedor_item">
    <div class="div_programas_imagen">
    <a href="/programas/buen-d%C3%ADa-uruguay">
    <img class="img-responsive" typeof="foaf:Image" src="http://www.montecarlotv.com.uy/sites/default/files/styles/imagen_programa/public/BDU%20406x246_0.jpg?itok=K06T-Tjx" width="406" height="246" alt="" />
    </a>
    </div>
    <div class="div_programas_descripcion">LUNES A VIERNES 8:30</div>
    <div class="div_programas_programa">
    <span><a href="/programas/buen-d%C3%ADa-uruguay">Buen día Uruguay</a></span>
    </div></div></div>
    '''
    '''
    <div class="col-lg-4 col-md-4 col-sm-6 col-xs-12">
    <div class="div_programas_contenedor_item">
    <div class="div_programas_imagen">
    <a href="/programas/el-secreto-de-feriha">
    <img class="img-responsive" typeof="foaf:Image" src="http://www.montecarlotv.com.uy/sites/default/files/styles/imagen_programa/public/El%20secreto%20de%20Feriha%20406x246.jpg?itok=_9ewAd6n" width="406" height="246" alt="" />
    </a></div>
    <div class="div_programas_descripcion">LUNES A VIERNES 18:00</div>
    <div class="div_programas_programa_largo">
    <span><a href="/programas/el-secreto-de-feriha">El Secreto de Feriha</a></span>
    </div></div></div>
    '''
    data = scrapertools.cachePage(item.url)

    patron = '<div class="div_programas_contenedor_item"[^<]+'
    patron += '<div class="div_programas_imagen"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img class="img-responsive" typeof="foaf:Image" src="([^"]+)"[^<]+'
    patron += '</a[^<]+'
    patron += '</div[^<]+'
    patron += '<div class="div_programas_descripcion">([^<]+)</div[^<]+'
    patron += '<div class="div_programas_programa[^<]+'
    patron += '<span><a href="[^"]+">([^<]+)</a></span[^<]+'

    matches = re.findall(patron,data,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedplot,scrapedtitle in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url,scrapedurl)
        url = url+"/"
        url = urlparse.urljoin(url,"videos-historicos")
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = scrapedplot
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=CHANNELNAME, title=title , action="episodios" , url=url, thumbnail=thumbnail, plot=plot, show=title) )

    return itemlist

def episodios(item, load_all_pages=False):
    logger.info("tvalacarta.channels.montecarlo episodios")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    '''
    <div class="col-lg-4 col-md-6 col-sm-6 col-xs-12">
    <div class="div_videos_contenedor_item">
    <div class="div_videos_imagen">
    <a href="/programas/el-sult%C3%A1n/videos/cap%C3%ADtulo-2">
    <img class="img-responsive" typeof="foaf:Image" src="http://www.montecarlotv.com.uy/sites/default/files/styles/imagen_programa/public/Sultan_20012016.jpg?itok=0rXaCnrn" width="406" height="246" alt="" />
    </a>
    </div> 
    <a href="/programas/el-sult%C3%A1n/videos/cap%C3%ADtulo-2">
    <div class="div_videos_contenedor_descripcion">
    <div class="div_videos_contenedor_descripcion_linea1">
    <div class="div_videos_fecha">
    <span class="date-display-single" property="dc:date" datatype="xsd:dateTime" content="2016-01-20T00:00:00-03:00">20/01/2016</span>
    </div></div><div class="div_videos_titulo">Capítulo 2</div></div></a>
    '''
    patron  = '<div class="div_videos_contenedor_item"[^<]+'
    patron += '<div class="div_videos_imagen"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img class="img-responsive" typeof="foaf:Image" src="([^"]+)"[^<]+'
    patron += '</a[^<]+'
    patron += '</div>[^<]+'
    patron += '<a[^<]+'
    patron += '<div class="div_videos_contenedor_descripcion[^<]+'
    patron += '<div class="div_videos_contenedor_descripcion[^<]+'
    patron += '<div class="div_videos_fecha[^<]+'
    patron += '<span class="date-display-single[^>]+>([^<]+)</span[^<]+'
    patron += '</div></div><div class="div_videos_titulo">([^<]+)<'

    matches = re.findall(patron,data,re.DOTALL)

    for scrapedurl,scrapedthumbnail,scrapedfecha,scrapedtitle in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = ""
        aired_date = scrapertools.parse_date(scrapedfecha)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=CHANNELNAME, title=title , action="play" , server="montecarlo" , url=url, thumbnail=thumbnail, plot=plot, show=item.show, aired_date=aired_date, folder=False) )

    next_page_url = scrapertools.find_single_match(data,'<a title="Ir a la p[^"]+" href="([^>]+)">siguiente')
    if next_page_url!="":
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , action="episodios" , url=urlparse.urljoin(item.url,next_page_url), show=item.show) )

    return itemlist

def detalle_programa(item):

    item.plot = scrapertools.find_single_match(data,'<div class="div_slider_descripcion">([^<]+)</div>')+"\n"+item.plot

    return item

def detalle_episodio(item):

    data = scrapertools.cache_page(item.url)

    scrapedplot = scrapertools.find_single_match(data,'<div class="div_video_field_body"><div class="field-content"><p class="rtejustify"><spa[^>]+>(.*?)</')
    scrapedthumbnail = scrapertools.find_single_match(data,'image\:\s*"([^"]+)"')

    item.plot = scrapertools.htmlclean( scrapedplot ).strip()
    item.thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)

    item.geolocked = "0"
    
    try:
        from servers import montecarlo as servermodule
        video_urls = servermodule.get_video_url(item.url,page_data=data)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def play(item):

    item.server="montecarlo";
    itemlist = [item]

    return itemlist
