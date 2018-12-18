# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Extremadura TV
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "extremaduratv"
URL_DIRECTO = "http://hlstv.canalextremadura.es/livetv/smil:multistream.smil/playlist.m3u8"

def isGeneric():
    return True

def mainlist(item, load_all_pages=False):
    logger.info("tvalacarta.channels.extremaduratv.mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Programas"      , action="programas"    , url="http://www.canalextremadura.es/tv/programas", category="programas") )
    itemlist.append( Item(channel=CHANNELNAME, title="Archivo"        , action="programas"      , url="http://www.canalextremadura.es/tv/archivo", category="programas") )
    itemlist.append( Item(channel=CHANNELNAME, title="Directo"        , action="play"      , extra=URL_DIRECTO, category="programas", folder=False) )

    return itemlist

def directos(item=None):
    logger.info("tvalacarta.channels.extremaduratv directos")

    itemlist = []

    itemlist.append( Item(channel=CHANNELNAME, title="Extremadura TV",   url=URL_DIRECTO, thumbnail="http://media.tvalacarta.info/canales/128x128/extremaduratv.png", category="Autonómicos", action="play", folder=False ) )

    return itemlist

def programas(item, load_all_pages=False):
    logger.info("tvalacarta.channels.extremaduratv.programas")
    itemlist = []

    # Descarga la página
    '''
    div class="entry-image nomargin">
    <a href="/tv/informativos/extremadura-noticias-1">
    <img class="image_fade" src="/sites/default/files/styles/nuevo_dise_o_-_mediana/public/imagenes-nuevo-disenio
    /programas/extremadura_noticias_1.jpg?itok=nw-nIIrz" alt="Extremadura Noticias 1" onerror="this.src='
    /sites/default/files/logotipo-400x225.jpg'">

    <div class="panel panel-default opacity-90 noradius topmargin-xxs">
    <div class="panel-body">
    <h4 class="nomargin max-lines max-2-lines">Extremadura Noticias 1</h4>
    '''
    data = scrapertools.cachePage(item.url)
    patron  = 'div class="entry-image nomargin"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img class="image_fade" src="([^"]+)" alt="([^"]+)"'
    matches = re.findall(patron,data,re.DOTALL)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = ""
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="episodios" , url=url, thumbnail=thumbnail, fanart=thumbnail, show=title) )

    if len(itemlist)>0:
        if "page=" in item.url:
            current_page = scrapertools.find_single_match(item.url,"page=(\d+)")
            next_page = str(int(current_page)+1)
            next_page_url = item.url.replace("page="+current_page,"page="+next_page)
        else:
            next_page_url = item.url+"?page=2"

        next_page_item = Item(channel=CHANNELNAME, title=">> Página siguiente" , action="programas" , view="programs", url=next_page_url)

        if load_all_pages:
            itemlist.extend( programas(next_page_item,load_all_pages) )
        else:
            itemlist.append( next_page_item )

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
        item.plot = scrapertools.find_single_match(data,'<meta property="og:description" content="([^<]+)"')
        item.plot = scrapertools.decodeHtmlentities(item.plot)
        item.plot = scrapertools.htmlclean(item.plot).strip()
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def episodios(item):
    logger.info("tvalacarta.channels.extremaduratv.episodios")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    # En la primera página debe parsear los destacados
    if "?page" not in item.url:
        patron  = '<div class="ipost clearfix">(.*?<li><i class="icon-calendar3"></i[^<]+<span class="date-display-single">[^<]+</span>)'
        matches = re.findall(patron,data,re.DOTALL)
        logger.info("matches="+repr(matches))

        for match in matches:

            title = scrapertools.find_single_match(match,'<h3[^>]+>([^<]+)</h3>').strip()
            url = urlparse.urljoin(item.url,scrapertools.find_single_match(match,'<a href="([^"]+)"'))
            thumbnail = urlparse.urljoin(item.url,scrapertools.find_single_match(match,'<img class="image_fade" src="([^"]+)"'))
            plot = ""
            aired_date = scrapertools.find_single_match(match,'<span class="date-display-single">([^<]+)</span>')
            aired_date = scrapertools.parse_date(aired_date).strip()
            if aired_date=="":
                aired_date = scrapertools.parse_date(title).strip()

            if title!="":
                itemlist.append( Item(channel=CHANNELNAME, title=title , action="play" , server="extremaduratv" , plot=plot, url=url, thumbnail=thumbnail, fanart=thumbnail, show=item.show, aired_date=aired_date, view="videos", folder=False) )



    patron  = '<div class="col-md-4 col-sm-4 col-xs-6">(.*?<li><i class="icon-calendar3"></i[^<]+<span class="date-display-single">[^<]+</span>)'
    matches = re.findall(patron,data,re.DOTALL)

    for match in matches:

        title = scrapertools.find_single_match(match,'<h4[^>]+>([^<]+)</h4>').strip()
        url = urlparse.urljoin(item.url,scrapertools.find_single_match(match,'<a href="([^"]+)"'))
        thumbnail = urlparse.urljoin(item.url,scrapertools.find_single_match(match,'<img class="image_fade" src="([^"]+)"'))
        plot = ""
        aired_date = scrapertools.find_single_match(match,'<span class="date-display-single">([^<]+)</span>')
        aired_date = scrapertools.parse_date(aired_date).strip()
        if aired_date=="":
            aired_date = scrapertools.parse_date(title).strip()

        if title!="":
            itemlist.append( Item(channel=CHANNELNAME, title=title , action="play" , server="extremaduratv" , plot=plot, url=url, thumbnail=thumbnail, fanart=thumbnail, show=item.show, aired_date=aired_date, view="videos", folder=False) )

    if len(itemlist)>0:
        next_page_url = scrapertools.find_single_match(data,'<li class="pager-next"><a title="[^"]+" href="([^"]+)"')
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        next_page_item = Item(channel=CHANNELNAME, title=">> Página siguiente" , action="episodios" , url=next_page_url)
        itemlist.append( next_page_item )

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    
    # Todas las opciones tienen que tener algo
    items = mainlist(Item())
    for item in items:
        exec "itemlist="+item.action+"(item)"
    
        if len(itemlist)==0:
            print "La categoria '"+item.title+"' no devuelve programas"
            return False

    # El primer programa de la primera categoria tiene que tener videos
    mainlist_items = mainlist(Item())
    programas_items = programas(mainlist_items[0])
    submenu_episodios_items = episodios(programas_items[0])

    exec "episodios_itemlist="+submenu_episodios_items[0].action+"(submenu_episodios_items[0])"
    if len(episodios_itemlist)==0:
        print "El programa '"+programas_mainlist[0].title+"' no tiene videos en su seccion '"+submenu_episodios_items[0].title+"'"
        return False

    return True
