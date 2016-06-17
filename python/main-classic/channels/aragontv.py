# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Aragón TV
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import datetime
import time

from core import logger
from core import config
from core import scrapertools
from core.item import Item

DEBUG = config.get_setting("debug")
CHANNELNAME = "aragontv"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.aragontv mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Últimos vídeos añadidos" , url="http://alacarta.aragontelevision.es/por-fecha/" , action="episodios" , folder=True, view="videos") )
    itemlist.append( Item(channel=CHANNELNAME, title="Informativos" , url="http://alacarta.aragontelevision.es/informativos" , action="episodios" , folder=True, view="videos") )
    itemlist.append( Item(channel=CHANNELNAME, title="Todos los programas" , url="http://alacarta.aragontelevision.es/programas" , action="programas" , folder=True, view="programs") )
    itemlist.append( Item(channel=CHANNELNAME, title="Buscador" , action="search" , folder=True, view="videos") )

    return itemlist

def search(item,texto):
    logger.info("tvalacarta.channels.aragontv search")
    itemlist = []
    
    item.url = "http://alacarta.aragontelevision.es/buscador-avanzado/resultados-buscados_1/?palabra="+urllib.quote(texto)+"&buscar="
    return episodios(item)

def ultimos(item):
    logger.info("tvalacarta.channels.aragontv programas [item="+item.tostring()+" show="+item.show+"]")

    # Descarga la página
    post = urllib2.urlencode({"fechaCabecera":time.strftime("%d-%m-%Y")})
    data = scrapertools.cachePage(item.url,post=post)

    itemlist=episodios(item,data)

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.aragontv programas [item="+item.tostring()+" show="+item.show+"]")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    #logger.info(data)

    # Extrae las entradas
    '''
    <div class="bloque">
    <img src="/_archivos/imagenes/oregon-tv_735.png" width="290" height="150" alt="OREGÓN TELEVISIÓN" title="OREGÓN TELEVISIÓN" />
    <h3><a href="/programas/oregon-tv/" title="OREGÓN TELEVISIÓN"><strong>OREGÓN TELEVISIÓN</strong></a></h3>
    <p style="float:left; width: 100%;">Nuestro programa de humor más &quot;oregonés&quot;</p>
    <a href="/programas/oregon-tv/" class="button align" title="Ver videos"><span>Ver videos</span></a>
    </div>
    '''
    patron  = '<div class="bloque[^<]+'
    patron += '<img src="([^"]+)"[^>]+>[^<]+'
    patron += '<h3><a href="([^"]+)"[^>]+><strong>([^<]+)</strong></a></h3>[^<]+'
    patron += '<p[^>]+>([^<]+)</p>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    #if DEBUG: scrapertools.printMatches(matches)

    itemlist = []
    for match in matches:
        scrapedtitle = match[2]

        scrapedurl = urlparse.urljoin(item.url,match[1])
        scrapedthumbnail = urlparse.urljoin(item.url,match[0])
        scrapedplot = match[3]
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        if not "programas/vaughan" in scrapedurl:
            # Añade al listado
            itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot , show=scrapedtitle, folder=True) )
        else:
            itemlist.extend( subcategorias(scrapedurl) )

    return itemlist

def episodios(item,data=""):
    logger.info("tvalacarta.channels.aragontv episodios")
    logger.info("tvalacarta.channels.aragontv programa [item="+item.tostring()+" show="+item.show+"]")
    itemlist = []

    # Descarga la página
    if data=="":
        data = scrapertools.cachePage(item.url)

    # Extrae las entradas
    '''
    <div id="idv_1186" class="vid bloque">
    <div class="imagen">
    <img title="Malanquilla y Camarillas" alt="Malanquilla y Camarillas" src="/_archivos/imagenes/galeria_5738_thumb.jpg" />			        
    <div class="play">
    <a href="/programas/pequeños-pero-no-invisibles/malanquilla-y-camarillas-27122011-2131" title="Ver video" rel="videoFacebox"><span>Ver video</span></a>
    </div>
    </div>
    <h2><a href="/programas/pequeños-pero-no-invisibles/malanquilla-y-camarillas-27122011-2131" title="Malanquilla y Camarillas" rel="videoFacebox">Malanquilla y Camarillas</a></h2>
    
    <!--<br><a href="/programas/pequeños-pero-no-invisibles/malanquilla-y-camarillas-27122011-2131" title="Malanquilla y Camarillas" rel="videoFacebox2">Malanquilla y Camarillas</a> -->
    <div class="social">
    <span class="fecha">
    27/12/2011 21:31 h<br />
    Duración: 00:49:38
    </span>
    </div>
    </div>
    '''
    patron  = '<div id="[^"]+" class="vid bloque[^<]+'
    patron += '<div class="imagen[^<]+'
    patron += '<img title="[^"]+" alt="([^"]+)" src="([^"]+)"[^<]+'
    patron += '<div class="play">[^<]+'
    patron += '<a href="([^"]+)".*?'
    patron += '<span class="fecha">(.*?)</span>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    #if DEBUG: scrapertools.printMatches(matches)

    itemlist = []
    for match in matches:
        # Interpreta la fecha
        patron_fecha = "\s*([^<]+)<br />\s*Duración\: ([^\s]+)"
        campos_fecha =re.compile(patron_fecha,re.DOTALL).findall(match[3])
        fecha_string = campos_fecha[0][0].strip()
        #import time
        #fecha = time.strptime(fecha_string,"%d/%m/%y %H:%M")
        duracion_string = campos_fecha[0][1].strip()

        aired_date = scrapertools.parse_date(fecha_string)
        duration = duracion_string

        #scrapedtitle = match[0]+" "+fecha.strftime("%d/%m/%y")+" (Duración "+duracion_string+")"
        scrapedtitle = match[0].strip()
        scrapedurl = urlparse.urljoin(item.url,match[2])
        scrapedthumbnail = urlparse.urljoin(item.url,match[1])
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"], show=["+item.show+"]")

        # Añade al listado
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , server="aragontv" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , show=item.show, aired_date=aired_date, duration=duration, folder=False) )

    patron  = "Paginación.*?<span class='activo'>[^<]+</span>  \|  <a href='([^']+)'"
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches)>0:
        pageitem = Item(channel=CHANNELNAME, title=">> Página siguiente" , action="episodios" , url=urlparse.urljoin(item.url,matches[0]), thumbnail=item.thumbnail, plot=item.plot , show=item.show, folder=True, view="videos")
        itemlist.append( pageitem )

    return itemlist

def detalle_episodio(item):

    data = scrapertools.cache_page(item.url)

    scrapedplot = scrapertools.find_single_match(data,'<span class="title">Resumen del v[^>]+</span>(.*?)</div>')
    item.plot = scrapertools.htmlclean( scrapedplot ).strip()
    item.title = scrapertools.find_single_match(data,'<span class="activo"><strong>([^<]+)</strong></span>')
    item.aired_date = scrapertools.parse_date( item.title )

    item.geolocked = "0"
    
    try:
        from servers import aragontv as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def subcategorias(pageurl):
    logger.info("tvalacarta.channels.aragontv subcategorias")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(pageurl)
    #logger.info(data)

    # Extrae las entradas
    '''
    <td colspan="2"><a href="http://alacarta.aragontelevision.es/programas/vaughan/basico-i" target="_blank"><img style="FLOAT: left" src="http://alacarta.aragontelevision.es/_archivos/ficheros/basico%20I_201.png" alt="" /></a></td>
    '''
    patron  = '<td colspan[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img.*?src="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    itemlist = []
    for url,thumbnail in matches:
        scrapedtitle = scrapertools.get_match(url,'programas/(vaughan/.*?)$').replace("/"," ").upper()
        scrapedurl = urlparse.urljoin(pageurl,url)
        scrapedthumbnail = thumbnail
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot , show=scrapedtitle, folder=True, view="videos") )

    return itemlist

# Test de canal
# Devuelve: Funciona (True/False) y Motivo en caso de que no funcione (String)
def test():
    
    items_mainlist = mainlist(Item())
    items_programas = programas(items_mainlist[2])

    # El canal tiene estructura programas -> episodios -> play
    if len(items_programas)==0:
        return False,"No hay programas"

    items_episodios = episodios(items_programas[0])
    if len(items_episodios)==0:
        return False,"No hay episodios en "+items_programas[0].title

    item_episodio = detalle_episodio(items_episodios[0])
    if item_episodio.media_url=="":
        return False,"El conector no devuelve enlace para el vídeo "+item_episodio.title

    return True,""
