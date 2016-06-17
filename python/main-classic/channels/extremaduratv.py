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

def mainlist(item):
    logger.info("extremaduratv.mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Informativos"   , action="programas"    , url="http://www.canalextremadura.es/alacarta/tv/programas/informativos", category="informativos") )
    itemlist.append( Item(channel=CHANNELNAME, title="Programas"      , action="programas"    , url="http://www.canalextremadura.es/alacarta/tv/programas/programas", category="programas") )
    itemlist.append( Item(channel=CHANNELNAME, title="Deportes"       , action="programas"    , url="http://www.canalextremadura.es/alacarta/tv/programas/deportes", category="deportes") )
    itemlist.append( Item(channel=CHANNELNAME, title="Archivo"        , action="archivo"      , url="http://www.canalextremadura.es/alacarta/tv/programas/archivo", category="programas") )

    return itemlist

def programas(item):
    logger.info("extremaduratv.programas")
    itemlist = []

    # Descarga la página
    '''
    <div class="views-field views-field-field-programa-a-la-carta">
    <div class="field-content">
    <a href="/alacarta/tv/programas/programas/76148/52-minutos" title="Título del enlace"><div class="field-content"><img src="http://www.canalextremadura.es/sites/default/files/styles/alacarta_listado_programas/public/52_minutos_535-290.jpg?itok=E4F3DF9z" width="225" height="140" alt="" /></div></a>    </div>
    </div>
    <div class="views-field views-field-title">
    <div class="field-content">
    <a href="/alacarta/tv/programas/programas/76148/52-minutos" title="Título del enlace">52 minutos</a>    </div>
    '''
    data = scrapertools.cachePage(item.url)
    patron  = '<div class="views-field views-field-field-programa-a-la-carta"[^<]+'
    patron += '<div class="field-content"[^<]+'
    patron += '<a href="([^"]+)"[^<]+<div class="field-content"><img src="([^"]+)"[^<]+</div></a[^<]+</div[^<]+'
    patron += '</div[^<]+'
    patron += '<div class="views-field views-field-title"[^<]+'
    patron += '<div class="field-content"[^<]+'
    patron += '<a[^>]+>([^<]+)</a>'

    matches = re.findall(patron,data,re.DOTALL)

    for url,thumbnail,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = urlparse.urljoin(item.url,thumbnail)
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, show=scrapedtitle) )

    return itemlist

def archivo(item):
    logger.info("extremaduratv.archivo")
    itemlist = []

    # Descarga la página
    '''
    <div class="views-field views-field-field-programa-a-la-carta col-xs-7">
    <div class="field-content">
    <a href="/alacarta/tv/programas/programas/1027/castillos-de-extremadura" title="Título del enlace">
    <div class="field-content">
    <a href="/tv/programas/castillos-de-extremadura">
    <img src="http://www.canalextremadura.es/sites/default/files/styles/alacarta_categorias_programas_archivo/public/foto_cabecera.jpg?itok=OMC1fjc4" width="75" height="46" alt="Ver ficha del programa" title="Ver ficha del programa" />
    </a></div></a>        </div>
    </div>
    <div class="views-field views-field-title col-xs-17">
    <div class="field-content">
    <a href="/alacarta/tv/programas/programas/1027/castillos-de-extremadura" title="Título del enlace">Castillos de Extremadura</a>        </div>
    '''
    data = scrapertools.cachePage(item.url)
    patron  = '<div class="views-field views-field-field-programa-a-la-carta[^<]+'
    patron += '<div class="field-content"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<div class="field-content"[^<]+'
    patron += '<a[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '</a></div></a[^<]+</div[^<]+'
    patron += '</div[^<]+'
    patron += '<div class="views-field views-field-title[^<]+'
    patron += '<div class="field-content"[^<]+'
    patron += '<a[^>]+>([^<]+)</a>'

    matches = re.findall(patron,data,re.DOTALL)

    for url,thumbnail,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = urlparse.urljoin(item.url,thumbnail)
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, show=scrapedtitle) )

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.url)
    url = scrapertools.find_single_match(data,'<a href="([^"]+)">Ficha del programa</a>')
    data = scrapertools.cache_page(urlparse.urljoin(item.url,url))

    item.plot = scrapertools.find_single_match(data,'<div class="descripcion-programa">(.*?)</div>')
    item.plot = scrapertools.htmlclean(item.plot).strip()

    item.thumbnail = scrapertools.find_single_match(data,'<div class="col-xs-8 col-right"[^<]+<img src="([^"]+)"')

    return item

def detalle_episodio(item):

    data = scrapertools.cache_page(item.url)

    scrapedplot = scrapertools.find_single_match(data,'<div class="descripcion">(.*?)</')

    '''
    http://iphonevod.canalextremadura.es/PROG00146680.mp4#550#300#/sites/default/files/vlcsnap-2015-09-18-13h10m49s47.png#true
    '''
    scrapedthumbnail = scrapertools.find_single_match(data,'data-iosUrl="([^"]+)">')

    item.plot = scrapertools.htmlclean( scrapedplot ).strip()

    try:
        item.thumbnail = urlparse.urljoin(item.url,scrapedthumbnail.split("#")[3])
    except:
        import traceback
        print traceback.format_exc()

    item.geolocked = "0"
    
    try:
        from servers import extremaduratv as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def episodios(item):
    logger.info("extremaduratv.episodios")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    # Si hay algo en el contenedor izquierdo
    titulo_bloque_izquierdo = scrapertools.find_single_match(data,'<div class="videos-izq"><h3>([^<]+)</h3>')
    titulo_bloque_derecho = scrapertools.find_single_match(data,'<div class="videos-der"><h3>([^<]+)</h3>')

    if titulo_bloque_izquierdo<>"" and titulo_bloque_derecho<>"":
        itemlist.append( Item(channel=CHANNELNAME, title=titulo_bloque_izquierdo , action="episodios_bloque_izquierdo", url=item.url, show=item.show, extra="completos", folder=True) )
        itemlist.append( Item(channel=CHANNELNAME, title=titulo_bloque_derecho , action="episodios_bloque_derecho", url=item.url, show=item.show, extra="fragmentos", folder=True) )
    else:
        if titulo_bloque_izquierdo<>"":
            itemlist = episodios_bloque_izquierdo(item)
        else:
            itemlist = episodios_bloque_derecho(item)

    return itemlist

def episodios_bloque_izquierdo(item):
    logger.info("extremaduratv.episodios_bloque_izquierdo")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data,'<div class="contenedor-izq(.*?)<div class="contenedor-der')

    patron  = '<li class="views-row[^<]+'
    patron += '<div class="views-field views-field-title"[^<]+'
    patron += '<span class="field-content"[^<]+'
    patron += '<a href="([^"]+)">([^<]+)</a>'

    matches = re.findall(patron,data,re.DOTALL)

    for url,titulo in matches:
        scrapedtitle = titulo.strip()
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = ""
        scrapedplot = ""

        # Trata de sacar la fecha de emisión del título
        aired_date = scrapertools.parse_date(scrapedtitle)

        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , server="extremaduratv" , url=scrapedurl, thumbnail = scrapedthumbnail, show=item.show, aired_date=aired_date, folder=False) )

    #<li class="pager-next last"><a href="/alacarta/tv/programas/informativos/97/extremadura-noticias-1?page=1" 
    patron = '<li class="pager-next[^<]+<a href="([^"]+)"'
    matches = re.findall(patron,data,re.DOTALL)

    for url in matches:
        scrapedurl = urlparse.urljoin(item.url,url)
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , action="episodios_bloque_izquierdo" , url=scrapedurl, show=item.show, extra=item.extra) )

    return itemlist

def episodios_bloque_derecho(item, load_all_pages=False):
    logger.info("extremaduratv.episodios_bloque_derecho")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    '''
    <a href="/alacarta/tv/videos/trastos-y-tesoros-260315">
    <img src="http://www.canalextremadura.es/sites/default/files/styles/alacarta_listado_programas/public/cadillac.jpg?itok=cAhwJKrp" width="225" height="140" alt="" />
    </a></div>  </div>  
    <div class="views-field views-field-title">        
    <span class="field-content">Trastos y tesoros (26/03/15)</span>
    '''
    patron  = '<a href="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '</a></div[^<]+</div[^<]+'
    patron += '<div class="views-field views-field-title"[^<]+'
    patron += '<span class="field-content">([^<]+)</span>'

    matches = re.findall(patron,data,re.DOTALL)

    for url,thumbnail,titulo in matches:
        scrapedtitle = titulo.strip()
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = thumbnail
        scrapedplot = ""

        # Trata de sacar la fecha de emisión del título
        aired_date = scrapertools.parse_date(scrapedtitle)

        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , server="extremaduratv" , url=scrapedurl, thumbnail = scrapedthumbnail, show=item.show, aired_date=aired_date, folder=False) )

    #<li class="pager-next last"><a href="/alacarta/tv/programas/informativos/97/extremadura-noticias-1?page=1" 
    next_page_url = scrapertools.find_single_match(data,'href="([^"]+)">siguiente')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        next_page_item = Item(channel=CHANNELNAME, title=">> Página siguiente" , action="episodios" , url=next_page_url, show=item.show, extra=item.extra)

        if load_all_pages:
            itemlist.extend(episodios(next_page_item,load_all_pages))
        else:
            itemlist.append( next_page_item )

    return itemlist

def play(item):

    item.server="extremaduratv";
    itemlist = [item]

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
