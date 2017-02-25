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

def isGeneric():
    return True

def mainlist(item, load_all_pages=False):
    logger.info("extremaduratv.mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Programas"      , action="programas"    , url="http://www.canalextremadura.es/tv/programas", category="programas") )
    itemlist.append( Item(channel=CHANNELNAME, title="Archivo"        , action="programas"      , url="http://www.canalextremadura.es/tv/archivo", category="programas") )
    itemlist.append( Item(channel=CHANNELNAME, title="ExtremaduraTV SAT en directo"        , action="play"      , extra="http://hlstv.canalextremadura.es/livetv/smil:multistream.smil/playlist.m3u8", category="programas") )

    return itemlist

def programas(item, load_all_pages=False):
    logger.info("extremaduratv.programas")
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

    #data = scrapertools.cachePage(item.url)

    item.media_url = item.extra #scrapertools.find_single_match(data,'file\:\s+"([^"]+)"')

    return item

def episodios(item):
    logger.info("extremaduratv.episodios")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    '''
    <div class="modal-video-ajax modal-video modal fade color-tv" id="modalTV2_33318" tabindex="-1" role="dialog" aria-labelledby="modalTV2_33318Label" aria-hidden="true"
    data-video-imagen-modal="http://www.canalextremadura.es/sites/default/files/styles/nuevo_dise_o_-_grande/public/imagenes-nuevo-disenio/tv-a-la-carta/_desdeelaire.jpg?itok=FmvSbPkH"
    data-video-video-mobile="http://iphonevod.canalextremadura.es/S-B4583-009.mp4"
    data-video-url="/alacarta/tv/videos/extremadura-desde-el-aire-3"
    data-video-titulo-modal="El Reino del Pata Negra"
    data-video-id-nodo="33318"
    data-video-video-modal="rtmp://canalextremadura.cdn.canalextremadura.es/canalextremadura/tv/S-B4583-009.mp4"
    '''
    patron  = '<div class="modal-video-ajax(.*?<div class="barra-cerrar-modal)'
    matches = re.findall(patron,data,re.DOTALL)

    # Las páginas siguientes se saltan los dos primeros vídeos (son destacados que se repiten)
    if "?page" in item.url:
        saltar = 2
    else:
        saltar = 0

    for match in matches:

        if saltar>0:
            saltar = saltar - 1
            continue

        title = scrapertools.find_single_match(match,'data-video-titulo-modal="([^"]+)"')
        url = urlparse.urljoin(item.url,scrapertools.find_single_match(match,'data-video-url="([^"]+)"'))
        thumbnail = urlparse.urljoin(item.url,scrapertools.find_single_match(match,'data-video-imagen-modal="([^"]+)"'))
        plot = scrapertools.find_single_match(match,'<blockquote class="nomargin">(.*?)</blockquote>').strip()
        aired_date = scrapertools.parse_date(title)
        extra = urlparse.urljoin(item.url,scrapertools.find_single_match(match,'data-video-video-modal="([^"]+)"'))

        itemlist.append( Item(channel=CHANNELNAME, title=title , action="play" , server="extremaduratv" , plot=plot, url=url, thumbnail=thumbnail, fanart=thumbnail, show=item.show, aired_date=aired_date, extra=extra, view="videos", folder=False) )

    if len(itemlist)>0:
        next_page_url = scrapertools.find_single_match(data,'<li class="pager-next"><a title="[^"]+" href="([^"]+)"')
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        next_page_item = Item(channel=CHANNELNAME, title=">> Página siguiente" , action="episodios" , url=next_page_url)
        itemlist.append( next_page_item )

    return itemlist

def play(item,page_data=""):
    logger.info("tvalacarta.channels.extremaduratv play")

    itemlist = []

    if item.extra<>"":
        itemlist.append( Item(channel=CHANNELNAME, title=item.title , action="play" , server="directo" , url=item.extra, thumbnail=item.thumbnail, plot=item.plot , show=item.show , folder=False) )

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
