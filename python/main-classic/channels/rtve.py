# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para RTVE
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse, re

from core import config
from core import logger
from core import scrapertools
from core.item import Item

logger.info("[rtve.py] init")

DEBUG = True
CHANNELNAME = "rtve"

def isGeneric():
    return True

def mainlist(item):
    logger.info("[rtve.py] mainlist")

    itemlist = []
    
    # El primer nivel de menú es un listado por canales
    itemlist.append( Item(channel=CHANNELNAME, title="Directos"          , action="loadlives", folder=True))
    itemlist.append( Item(channel=CHANNELNAME, title="Todas las cadenas" , action="canal" , thumbnail = "" , url="http://www.rtve.es/alacarta/tve/", extra="tve"))
    itemlist.append( Item(channel=CHANNELNAME, title="La 1"              , action="canal" , thumbnail = "" , url="http://www.rtve.es/alacarta/tve/la1/", extra="la1"))
    itemlist.append( Item(channel=CHANNELNAME, title="La 2"              , action="canal" , thumbnail = "" , url="http://www.rtve.es/alacarta/tve/la2/", extra="la2"))
    itemlist.append( Item(channel=CHANNELNAME, title="Canal 24 horas"    , action="canal" , thumbnail = "" , url="http://www.rtve.es/alacarta/tve/24-horas/", extra="24-horas"))
    itemlist.append( Item(channel=CHANNELNAME, title="Teledeporte"       , action="canal" , thumbnail = "" , url="http://www.rtve.es/alacarta/tve/teledeporte/", extra="teledeporte"))

    return itemlist

def loadlives(item):
    logger.info("tvalacarta.channels.rtve play loadlives")

    itemlist = []

    url_la1 = "rtmp://rtvegeofs.fplive.net:1935/rtvegeoargmex-live-live/RTVE_LA1_LV3_WEB_GL7 swfUrl=http://swf.rtve.es/swf/4.3.13/RTVEPlayerVideo.swf pageUrl=http://www.rtve.es/directo/la-1/ live=true swfVfy=true"
    url_la2 = "rtmp://rtvefs.fplive.net:1935/rtve-live-live/RTVE_LA2_LV3_WEB_GL0 swfUrl=http://swf.rtve.es/swf/4.3.13/RTVEPlayerVideo.swf pageUrl=http://www.rtve.es/directo/la-2/ live=true swfVfy=true"
    url_tld = "rtmp://rtvegeofs.fplive.net:1935/rtvegeo-live-live/RTVE_TDP_LV3_WEB_GL1 swfUrl=http://swf.rtve.es/swf/4.3.13/RTVEPlayerVideo.swf pageUrl=http://www.rtve.es/directo/teledeporte/ live=true swfVfy=true"
    url_24h = "rtmp://rtvefs.fplive.net:443/rtve2-live-live/RTVE_24H_LV3_WEB_GL8 swfUrl=http://swf.rtve.es/swf/4.3.13/RTVEPlayerVideo.swf pageUrl=http://www.rtve.es/directo/canal-24h/ live=true swfVfy=true"
    # Radio
    url_rne = "http://radio1-fme.rtve.stream.flumotion.com/rtve/radio1.mp3.m3u"
    url_cls = "http://radioclasica-fme.rtve.stream.flumotion.com/rtve/radioclasica.mp3.m3u"
    url_rd3 = "http://radio3-fme.rtve.stream.flumotion.com/rtve/radio3.mp3.m3u"
    url_rd4 = "http://radio4-fme.rtve.stream.flumotion.com/rtve/radio4.mp3.m3u"
    url_rd5 = "http://radio5-fme.rtve.stream.flumotion.com/rtve/radio5.mp3.m3u"
    url_rex = "http://radioexterior-fme.rtve.stream.flumotion.com/rtve/radioexterior.mp3.m3u"

    itemlist.append( Item(channel=CHANNELNAME, title="La 1",        action="play", url=url_la1, folder=False) )
    itemlist.append( Item(channel=CHANNELNAME, title="La 2",        action="play", url=url_la2, folder=False) )
    itemlist.append( Item(channel=CHANNELNAME, title="Teledeporte", action="play", url=url_tld, folder=False) )
    itemlist.append( Item(channel=CHANNELNAME, title="Canal 24H",   action="play", url=url_24h, folder=False) )

    # Radio
    itemlist.append( Item(channel=CHANNELNAME, title="Radio: Radio Nacional", action="play", url=url_rne, folder=False) )
    itemlist.append( Item(channel=CHANNELNAME, title="Radio: Radio Clásica",  action="play", url=url_cls, folder=False) )
    itemlist.append( Item(channel=CHANNELNAME, title="Radio: Radio 3",        action="play", url=url_rd3, folder=False) )
    itemlist.append( Item(channel=CHANNELNAME, title="Radio: Radio 4",        action="play", url=url_rd4, folder=False) )
    itemlist.append( Item(channel=CHANNELNAME, title="Radio: Radio 5",        action="play", url=url_rd5, folder=False) )
    itemlist.append( Item(channel=CHANNELNAME, title="Radio: Radio Exterior", action="play", url=url_rex, folder=False) )

    return itemlist

def canal(item):
    logger.info("[rtve.py] canal")

    itemlist = []
    # El segundo nivel de menú es un listado por categorías
    itemlist.append( Item(channel=CHANNELNAME, title="Destacados" , action="destacados" , url=item.url , extra=item.extra))
    itemlist.append( Item(channel=CHANNELNAME, title="Todos los programas" , action="programas" , url="" , extra=item.extra+"/todos/1"))

    # Descarga la página que tiene el desplegable de categorias de programas
    url = "http://www.rtve.es/alacarta/programas/tve/todos/1/"
    data = scrapertools.cachePage(url)

    # Extrae las categorias de programas
    patron  = '<li><a title="Seleccionar[^"]+" href="/alacarta/programas/tve/([^/]+)/1/"><span>([^<]+)</span></a></li>'
    matches = re.findall(patron,data,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    # Crea una lista con las entradas
    for match in matches:
        scrapedtitle = match[1]
        scrapedurl = match[1]
        scrapedthumbnail = ""
        scrapedplot = ""
        scrapedextra = match[0]
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="programas" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra = item.extra + "/" + scrapedextra + "/1" , category = scrapedtitle ) )
    
    return itemlist

def destacados(item):
    logger.info("[rtve.py] destacados")
    itemlist = []

    data = scrapertools.cachePage(item.url)
    '''
    <div class="dest_title">Destacados versi&iquest;n libre</div>
    <div class="dest_page oculto">        <div  bourne:iseditable="false" class="unit c100 last">            <div  class="unit c100 last"><div class="mark">
    <div class="news  comp">
    <span class="tipo video">v&iacute;deo</span><span class="imgT"><a href="/alacarta/videos/informe-semanal/informe-semanal-soberanismo-suspenso/1814688/" title="Informe Semanal - Soberanismo en suspenso"><img src="http://img.irtve.es/imagenes/jpg/1368305081366.jpg" alt="Imagen Informe Semanal - Soberanismo en suspenso" title="Informe Semanal - Soberanismo en suspenso"/></a></span>
    </div>
    </div>
    </div>          </div>      </div>        <div class="dest_title">Destacados versi&iquest;n libre</div>    <div class="dest_page oculto">        <div  bourne:iseditable="false" class="unit c100 last">            <div  class="unit c100 last">              <div class="mark"><div class="news  comp"><span class="tipo video">v&iacute;deo</span><span class="imgT"><a href="/alacarta/videos/completos/cuentame-cap-251-150313/1768614/" title="Cu&eacute;ntame c&oacute;mo pas&oacute; - T14 - No hay cuento de Navidad - C
    '''
    logger.info("data="+data)
    patron  = '<div class="dest_title[^<]+</div[^<]+'
    patron += '<div class="dest_page oculto"[^<]+<div[^<]+<div[^<]+<div[^<]+'
    patron += '<div class="news[^<]+'
    patron += '<span class="tipo.*?</span><span class="imgT"><a href="([^"]+)" title="([^"]+)"><img src="([^"]+)"'

    matches = re.findall(patron,data,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        url=urlparse.urljoin(item.url,scrapedurl)
        title=scrapertools.htmlclean(scrapedtitle)
        thumbnail=scrapedthumbnail
        thumbnail = thumbnail.replace("&amp;","&")
        plot=""

        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        try:
            logger.info("url="+url)

            #http://www.rtve.es/alacarta/videos/cocina-con-sergio/cocina-sergio-quiche-cebolla-queso-curado/1814210/
            episodio = scrapertools.get_match(url,'http\://www.rtve.es/alacarta/videos/[^\/]+/([^\/]+)/')
            logger.info("es episodio")
            itemlist.append( Item(channel=CHANNELNAME, title=title , action="play" , server="rtve" , url=url, thumbnail=thumbnail, plot=plot, fanart=thumbnail, folder=False) )
        except:
            logger.info("es serie")
            itemlist.append( Item(channel=CHANNELNAME, title=title , action="episodios" , url=url, thumbnail=thumbnail, plot=plot, fanart=thumbnail, folder=True) )

    return itemlist

def programas(item):
    logger.info("[rtve.py] programas")
    
    # En la paginación la URL vendrá fijada, si no se construye aquí la primera página
    if not item.url.startswith("http"):
        item.url = "http://www.rtve.es/alacarta/programas/"+item.extra+"/?pageSize=100&order=1&criteria=asc&emissionFilter=all"
    logger.info("[rtve.py] programas url="+item.url) 

    itemlist = []
    data = scrapertools.cachePage(item.url)
    itemlist.extend(addprogramas(item,data))
    salir = False

    while not salir:
        # Extrae el enlace a la página siguiente
        patron  = '<a name="paginaIR" href="[^"]+" class="active"><span>[^<]+</span></a>[^<]+'
        patron += '<a name="paginaIR" href="([^"]+)"><span>'
    
        matches = re.findall(patron,data,re.DOTALL)
        if DEBUG: scrapertools.printMatches(matches)

        if len(matches)>0:
            # Carga la página siguiente
            url = urlparse.urljoin(item.url,matches[0]).replace("&amp;","&")
            data = scrapertools.cachePage(url)
            
            # Extrae todos los programas
            itemlist.extend(addprogramas(item,data))
        else:
            salir = True

    return itemlist

def addprogramas(item,data):
    
    itemlist = []
    
    # Extrae los programas
    patron  = '<li class="[^"]+">.*?'
    patron += '<span class="col_tit" id="([^"]+)" name="progname">[^<]+'
    patron += '<a href="([^"]+)" title="Ver programa seleccionado">([^<]+)</a>[^<]+'
    patron += '</span>[^<]+'
    patron += '<span class="col_fec">([^<]+)</span>.*?'
    patron += '<span class="col_cat">([^<]*)</span>'
    matches = re.findall(patron,data,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    # Crea una lista con las entradas
    for match in matches:
        if config.get_setting("rtve.programa.extendido")=="true":
            scrapedtitle = match[2]+" (Ult. emisión "+match[3]+") ("+match[4]+")"
        else:
            scrapedtitle = match[2]
        scrapedurl = urlparse.urljoin(item.url,match[1])
        scrapedthumbnail = ""
        scrapedplot = ""#match[5]
        scrapedextra = match[0]
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra = scrapedextra, show=scrapedtitle, category = item.category) )

    return itemlist

def detalle_programa(item):
    
    data = scrapertools.cache_page(item.url)
    
    # Extrae plot
    patron  = '<p class="intro">(.*?)</div>'
    matches = re.findall(patron, data, re.DOTALL)
    if len(matches)>0:
        item.plot = scrapertools.htmlclean( matches[0] ).strip()

    # Extrae thumbnail
    patron  = '<span class="imgPrograma">.*?'
    patron += '<img title="[^"]+" alt="[^"]+" src="([^"]+)" />'
    matches = re.findall(patron, data, re.DOTALL)
    if len(matches)>0:
        item.thumbnail = urlparse.urljoin(item.url,matches[0])
    
    # Extrae title
    patron  = '<div class="false_cab">[^<]+'
    patron += '<h2>[^<]+'
    patron += '<a[^>]+>[^<]+'
    patron += '<span>([^<]+)</span>'
    matches = re.findall(patron, data, re.DOTALL)
    if len(matches)>0:
        item.title = matches[0].strip()
    
    return item

def episodios(item):
    logger.info("[rtve.py] episodios")

    # En la paginación la URL vendrá fijada, si no se construye aquí la primera página
    if item.url=="":
        # El ID del programa está en item.extra (ej: 42610)
        # La URL de los vídeos de un programa es
        # http://www.rtve.es/alacarta/interno/contenttable.shtml?ctx=42610&pageSize=20&pbq=1
        item.url = "http://www.rtve.es/alacarta/interno/contenttable.shtml?ctx="+item.extra+"&pageSize=20&pbq=1"

    itemlist = get_episodios(item,1)
    if len(itemlist)==0:
        itemlist = get_episodios_documentales(item,1)

    if len(itemlist)>0:
        if config.is_xbmc() and len(itemlist)>0:
            itemlist.append( Item(channel=item.channel, title=">> Opciones para esta serie", url=item.url, action="serie_options##episodios", thumbnail=item.thumbnail, extra = item.extra , show=item.show, folder=False))

    return itemlist

def get_episodios(item,recursion):
    logger.info("[rtve.py] get_episodios_documentales")

    itemlist = []
    data = scrapertools.cachePage(item.url)

    # Extrae los vídeos
    '''
    <li class="odd">
    <span class="col_tit" id="2851919" name="progname">
    <a href="/alacarta/videos/atencion-obras/atencion-obras-josep-maria-flotats-ferran-adria-sanchis-sinisterra/2851919/">Atención Obras - 07/11/14</a>
    </span>
    <span class="col_tip">
    <span>Completo</span>
    </span>
    <span class="col_dur">55:35</span>
    <span class="col_pop"><span title="32% popularidad" class="pc32"><em><strong><span>32%</span></strong></em></span></span>
    <span class="col_fec">07 nov 2014</span>

    <div id="popup2851919" class="tultip hddn"> 
    <span id="progToolTip" class="tooltip curved">
    <span class="pointer"></span>
    <span class="cerrar" id="close2851919"></span>
    <span class="titulo-tooltip"><a href="/alacarta/videos/atencion-obras/atencion-obras-josep-maria-flotats-ferran-adria-sanchis-sinisterra/2851919/" title="Ver Atención Obras - 07/11/14">Atención Obras - 07/11/14</a></span>
    <span class="fecha">07 nov 2014</span>
    <span class="detalle">Josep María Flotats&#160;trae al Teatro María Guerrero de Madrid&#160;&#8220;El juego del amor y del azar&#8221;&#160;de Pierre de Marivaux. Un texto que ya ha sido estrenado en el Teatre Nacional de Catalunya. C...</span>
    '''
    patron  = '<li class="[^"]+">.*?'
    patron += '<span class="col_tit"[^<]+'
    patron += '<a href="([^"]+)">(.*?)</a[^<]+'
    patron += '</span>[^<]+'
    patron += '<span class="col_tip"[^<]+<span>([^<]+)</span[^<]+</span[^<]+'
    patron += '<span class="col_dur">([^<]+)</span>.*?'
    patron += '<span class="col_fec">([^<]+)</span>.*?'
    patron += '<span class="detalle">([^>]+)</span>'
    
    matches = re.findall(patron,data,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    # Crea una lista con las entradas
    for match in matches:
        if not "developer" in config.get_platform():
            scrapedtitle = match[1]+" ("+match[2].strip()+") ("+match[3].strip()+") ("+match[4]+")"
        else:
            scrapedtitle = match[1]
        scrapedtitle = scrapedtitle.replace("<em>Nuevo</em>&nbsp;","")
        scrapedtitle = scrapertools.unescape(scrapedtitle)
        scrapedtitle = scrapedtitle.strip()
        scrapedurl = urlparse.urljoin(item.url,match[0])
        scrapedthumbnail = item.thumbnail
        scrapedplot = scrapertools.unescape(match[5].strip())
        scrapedplot = scrapertools.htmlclean(scrapedplot).strip()
        scrapedextra = match[2]
        
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , server="rtve" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , show=item.show, category = item.category, extra=scrapedextra, folder=False) )

    # Paginación

    if len(itemlist)>0:
        
        next_page_url = scrapertools.find_single_match(data,'<a name="paginaIR" href="([^"]+)"><span>Siguiente</span></a>')
        if next_page_url!="":
            next_page_url = urlparse.urljoin(item.url,next_page_url).replace("&amp;","&")
            #http://www.rtve.es/alacarta/interno/contenttable.shtml?pbq=2&modl=TOC&locale=es&pageSize=15&ctx=36850&advSearchOpen=false
            if not next_page_url.endswith("&advSearchOpen=false"):
                next_page_url = next_page_url + "&advSearchOpen=false"

            siguiente_item = Item(channel=CHANNELNAME,action="episodios",url=urlparse.urljoin(item.url,next_page_url),title=item.title,show=item.show,category=item.category)
            logger.info("siguiente_item="+siguiente_item.tostring())

            # Para evitar listas eternas, si tiene más de 3 páginas añade el item de "siguiente"
            if recursion<=3:
                itemlist.extend( get_episodios(siguiente_item,recursion+1) )
            else:
                siguiente_item.title=">> Página siguiente"
                itemlist.append(siguiente_item)

    return itemlist

def get_episodios_documentales(item,recursion):
    logger.info("[rtve.py] get_episodios_documentales")

    itemlist = []
    data = scrapertools.cachePage(item.url)

    # Cabecera
    '''
    <div class="mark">
    <a title="Valencia" href="http://www.rtve.es/alacarta/videos/a-vista-de-pajaro/vista-pajaro-valencia/3165763/" alt="Valencia">
    <span class="ima f16x9 T">
    <img src="http://img.irtve.es/v/3165763/?w=800&amp;h=451&amp;crop=si"></span>
    <span class="textBox mantitle">Valencia</span>
    </a>
    <span class="textBox">
    <span class="hourdata">27:50</span>
    <span class="separata"> </span>
    <span class="datedata">17 junio 2015</span>
    </span>
    <div class="textBox descript">
    <p><P>Programa que recorre desde el cielo las tierras de la provincia de Valencia.</P></p>
    <p></p>
    </div>
    </div>
    '''
    patron  = '<div class="mark"[^<]+'
    patron += '<a title="([^"]+)" href="([^"]+)"[^<]+'
    patron += '<span class="[^<]+'
    patron += '<img src="([^"]+)".*?'
    patron += '<span class="hourdata">([^<]+)</span[^<]+'
    patron += '<span class="separata[^<]+</span[^<]+'
    patron += '<span class="datedata">([^<]+)</span>(.*?)</div'
    
    matches = re.findall(patron,data,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)
    primera_url = ""

    # Crea una lista con las entradas
    for scrapedtitle,scrapedurl,scrapedthumbnail,duracion,fecha,plot in matches:
        title = scrapedtitle+" ("+duracion+")("+fecha+")"
        url = urlparse.urljoin(item.url,scrapedurl)
        primera_url = url
        plot = scrapertools.htmlclean(plot).strip()
        thumbnail = scrapedthumbnail
        
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="play" , server="rtve" , url=url, thumbnail=thumbnail, plot=plot , show=item.show, category = item.category, fanart=thumbnail, viewmode="movie_with_plot", folder=False) )

    # Items
    '''
    <div class="mark">
    <a href="/alacarta/videos/a-vista-de-pajaro/vista-pajaro-via-plata/2990389/" title="La Vía de la Plata">
    <span class="ima f16x9 T">
    <img src="http://img.rtve.es/v/2990389/?w=300&h=200&crop=no" alt="La Vía de la Plata">
    </span>
    <div class="apiCall mainTiTle">
    <h3><span>La Vía de la Plata</span></h3>
    </div>
    </a>
    <div class="apiCall data">
    <span class="time">27:37</span>
    <span class="date">22 sep 1991</span>
    </div>
    </div>
    '''
    patron  = '<div class="mark"[^<]+'
    patron += '<a href="([^"]+)" title="([^"]+)"[^<]+'
    patron += '<span class="[^<]+'
    patron += '<img src="([^"]+)".*?'
    patron += '<div class="apiCall summary"[^<]+'
    patron += '<p[^<]+'
    patron += '<span class="time">([^<]+)</span[^<]+'
    patron += '<span class="date">([^<]+)</span>([^<]+)<'
    
    matches = re.findall(patron,data,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    # Crea una lista con las entradas
    for scrapedurl,scrapedtitle,scrapedthumbnail,duracion,fecha,plot in matches:
        title = scrapedtitle+" ("+duracion+")("+fecha+")"
        url = urlparse.urljoin(item.url,scrapedurl)

        # A veces el vídeo de cabecera se repite en los items
        if url==primera_url:
            continue
        plot = plot.strip()
        thumbnail = scrapedthumbnail
        
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="play" , server="rtve" , url=url, thumbnail=thumbnail, plot=plot , show=item.show, category = item.category, fanart=thumbnail, viewmode="movie_with_plot", folder=False) )

    # Paginación

    if len(itemlist)>0:
        next_page_url = scrapertools.find_single_match(data,'<a title="Ver m[^"]+" href="([^"]+)"')
        if next_page_url!="":
            siguiente_item = Item(channel=CHANNELNAME,action="episodios",url=urlparse.urljoin(item.url,next_page_url),title=item.title,show=item.show,category=item.category)
            logger.info("siguiente_item="+siguiente_item.tostring())
            # Para evitar listas eternas, si tiene más de 3 páginas añade el item de "siguiente"
            if recursion<=3:
                itemlist.extend( get_episodios_documentales(siguiente_item,recursion+1) )
            else:
                siguiente_item.title=">> Página siguiente"
                itemlist.append(siguiente_item)

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    # Todas las opciones tienen que tener algo
    items = mainlist(Item())

    # Lista de series
    la1_items = canal(items[1])

    la1_destacados = destacados(la1_items[0])
    if len(la1_destacados)==0:
        print "No hay destacados de La1"
        return False

    la1_programas = programas(la1_items[1])
    if len(la1_programas)==0:
        print "No programas en La1"
        return False

    la1_episodios = episodios(la1_programas[0])
    if len(la1_episodios)==0:
        print "La serie "+la1_programas[0].title+" no tiene episodios en La1"
        return False

    return True
