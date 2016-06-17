# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para 7rm
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,re
import urllib

from core import logger
from core import scrapertools
from core.item import Item
from core import jsontools

logger.info("tvalacarta.channels.sieterm init")

DEBUG = True
CHANNELNAME = "sieterm"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.sieterm mainlist")

    return categorias(item)

def categorias(item):
    logger.info("tvalacarta.channels.sieterm categorias")

    itemlist = []

    data = scrapertools.cachePage("http://webtv.7tvregiondemurcia.es/")
    data = scrapertools.find_single_match(data,'<ul class="nav center">(.*?)</ul>')
    logger.info("tvalacarta.channels.sieterm data="+data)

    patron  = '<a href="([^"]+)" title="[^"]+">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.strip()

        if title=="Histórico":
            url = "http://www.rtrm.es/servlet/rtrm.servlets.ServletLink2?METHOD=LSTBLOGALACARTA&serv=BlogPortal2&sit=c,6"
            action = "programas_antiguos"
        else:
            url = urlparse.urljoin(item.url,scrapedurl)
            action = "programas"
        
        thumbnail = ""
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=CHANNELNAME, title=title , action=action , url=url, thumbnail=thumbnail, category=title, plot=plot, view="programs" ) )
    
    return itemlist

def programas(item, load_all_pages=False):
    logger.info("tvalacarta.channels.sieterm programas")

    itemlist = []

    data = scrapertools.cachePage(item.url)

    '''
    <div class="col-xs-12 col-sm-6 col-md-6 col-lg-4 coleccion">
    <a href="/entretenimiento/gente-como-tu/2016/viernes-19-de-febrero/" title="Gente como tú">
    <div class="row">
    <div class="col-xs-6 coleccion-image">
    <img src="http://statics.7tvregiondemurcia.es/uploads/2015/05/gentecomotu-320x180.jpg" class="img-responsive">
    </div>
    <div class="col-xs-6 coleccion-texto">
    <h3>Gente como tú</h3>
    <p>El magazine de las tardes de 7 TV se llama Gente como tú y lo presenta Antonio Hidalgo. Historias...</p>
    </div>
    '''

    patron  = '<div[^<]+'
    patron += '<a href="([^"]+)" title="([^"]+)"[^<]+'
    patron += '<div class="row"[^<]+'
    patron += '<div class="col-xs-6 coleccion-image"[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '</div[^<]+'
    patron += '<div class="col-xs-6 coleccion-texto"[^<]+'
    patron += '<h3[^<]+</h3>(.*?)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedplot in matches:

        title = scrapedtitle
        plot = scrapertools.htmlclean(scrapedplot).strip()
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        fanart = thumbnail
        page = url

        # Añade al listado de XBMC
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="temporadas" , url=url, thumbnail=thumbnail, fanart=fanart, category=item.category, plot=plot, show=title, page=page ) )
    
    next_page_url = scrapertools.find_single_match(data,'<li><a href="([^"]+)">SIGUIENTE</a><li>')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        next_page_item = Item(channel=CHANNELNAME, title=">> Página siguiente" , action="programas" , url=next_page_url, category=item.category, view="programs")

        if load_all_pages:
            itemlist.extend(programas(next_page_item,load_all_pages))
        else:
            itemlist.append( next_page_item )

    return itemlist

def temporadas(item, load_all_pages=False):
    logger.info("tvalacarta.channels.sieterm temporadas")

    itemlist = []

    data = scrapertools.cachePage(item.url)
    patron = '"ID"\:"(\d+)","post_title"\:"([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for temporada_id,temporada_title in matches:

        title = "Temporada "+temporada_title
        plot = ""
        thumbnail = item.thumbnail
        url = "http://webtv.7tvregiondemurcia.es/temporadasbrowser/getCapitulos/"+temporada_id+"/1/1/"
        fanart = thumbnail

        # Añade al listado de XBMC
        temporadaitem = Item(channel=CHANNELNAME, title=title , action="videos" , url=url, thumbnail=thumbnail, fanart=fanart, plot=plot, category=item.category, show=item.show, view="videos" )
        #itemlist.extend( videos(temporadaitem,load_all_pages) )
        itemlist.append(temporadaitem)
    
    return itemlist

def videos(item, load_all_pages=False):
    logger.info("tvalacarta.channels.sieterm videos")

    itemlist = []

    json_body = scrapertools.cachePage(item.url)
    json_object = jsontools.load_json(json_body)
    logger.info("tvalacarta.channels.sieterm json_object="+repr(json_object))

    for entry in json_object["episodes"]:
        logger.info("tvalacarta.channels.sieterm entry="+repr(entry))

        title = entry["post_title"]
        plot = entry["post_content"]
        thumbnail = entry["image"]
        url = urlparse.urljoin( item.url , entry["url"] )
        fanart = thumbnail

        # Trata de sacar la fecha de emisión del título
        aired_date = entry["post_date"][0:10]

        # Añade al listado de XBMC
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="play", server="sieterm" , url=url, thumbnail=thumbnail, fanart=fanart, plot=plot, show=item.show, aired_date=aired_date, viewmode="movie_with_plot", folder=False ) )
    
    if json_object["hasNext"]:

        # Extrae la página de la URL
        trozos = item.url.split("/")
        current_page = trozos[-2]

        # La aumenta
        next_page = int(current_page)+1
        trozos[-2] = str(next_page)

        # Y recompone la URL
        next_page_url = "/".join(trozos)
        next_page_item = Item(channel=CHANNELNAME, title=">> Página siguiente" , action="videos" , url=next_page_url, thumbnail=thumbnail, fanart=fanart, show=item.show, view="videos" )

        if load_all_pages:
            itemlist.extend(videos(next_page_item, load_all_pages))
        else:
            itemlist.append( next_page_item )

    return itemlist

def programas_antiguos(item, load_all_pages=False):
    logger.info("tvalacarta.channels.sieterm programas_antiguos load_all_pages=="+repr(load_all_pages))

    itemlist = []

    data = scrapertools.cachePage(item.url)
    
    # Extrae las entradas (carpetas)
    patron  = '<dt class="alacarta-video">[^<]+'
    patron += '<a href="([^"]+)">([^<]+)</a>[^<]+'
    patron += '</dt>[^<]+'
    patron += '<dd style="height:100%;overflow:hidden;">[^<]+'
    patron += '<a[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '</a>([^<]+)</dd>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    itemlist = []
    for match in matches:
        # Atributos del vídeo
        scrapedtitle = unicode( match[1].strip() , "iso-8859-1" , errors="ignore").encode("utf-8")
        scrapedurl = urlparse.urljoin(item.url,match[0]).replace("&amp;","&")
        scrapedthumbnail = urlparse.urljoin(item.url,match[2]).replace("&amp;","&")
        scrapedplot = unicode( match[3].strip() , "iso-8859-1" , errors="ignore").encode("utf-8")
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot , show=scrapedtitle , view="videos" ) )

    # Busca la página siguiente
    next_page_url = scrapertools.find_single_match(data,'<a class="list-siguientes" href="([^"]+)" title="Ver siguientes a la cartas">Siguiente</a>')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        next_page_item = Item(channel=CHANNELNAME, title=">> Página siguiente" , action="programas_antiguos" , url=next_page_url , folder=True)

        if load_all_pages:
            itemlist.extend(programas_antiguos(next_page_item,load_all_pages=True))
        else:
            itemlist.append( next_page_item )

    return itemlist

def episodios(item, load_all_pages=False):
    logger.info("tvalacarta.channels.sieterm episodios")

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    #logger.info(data)

    # Extrae los vídeos
    '''
    <dt class="alacarta-video"><a href="http://..." title="...">Murcianos por el mundo: Cracovia</a> · 12/05/2010 · (5411 veces visto)</dt>
    <dd style="height:100%; overflow:hidden">
    <a href="http://www.7rm.es/servlet/rtrm.servlets.ServletLink2?METHOD=DETALLEALACARTA&amp;sit=c,6,ofs,10&amp;serv=BlogPortal2&amp;orden=1&amp;idCarta=40&amp;mId=4182&amp;autostart=TV" title="Ver v&iacute;deo">
    <img src="http://mediateca.regmurcia.com/MediatecaCRM/ServletLink?METHOD=MEDIATECA&amp;accion=imagen&amp;id=4182" alt="Murcianos por el mundo: Cracovia" title="Murcianos por el mundo: Cracovia" style="width:95px" />
    </a>
    Esta semana nos desplazamos al sur de Polonia, a Cracovia y Wroclaw, para conocer cómo viven seis murcianos en una de las ciudades más importantes de Polonia y Patrimonio de la Humanidad.
    <a href="http://ficheros.7rm.es:3025/Video/4/1/4182_BAJA.mp4">
    <img src="/images/bajarArchivo.gif" alt="Descargar Archivo" title="Descargar Archivo" style="margin:0;padding:0 5px 0 0;vertical-align:middle;border:none" />
    </a>
    </dd>
    '''
  
    '''
    <dt class="alacarta-video"><a href="http://www.7rm.es/servlet/rtrm.servlets.ServletLink2?METHOD=DETALLEALACARTA&amp;sit=c,6,ofs,0&amp;serv=BlogPortal2&amp;orden=2&amp;idCarta=36&amp;mId=3214&amp;autostart=TV" title="Ver v&iacute;deo">De la tierra al mar</a> · 22/12/2009 · (1072 veces visto)</dt>
    <dd style="height:100%; overflow:hidden">
    <a href="http://www.7rm.es/servlet/rtrm.servlets.ServletLink2?METHOD=DETALLEALACARTA&amp;sit=c,6,ofs,0&amp;serv=BlogPortal2&amp;orden=2&amp;idCarta=36&amp;mId=3214&amp;autostart=TV" title="Ver v&iacute;deo">
    <img src="http://mediateca.regmurcia.com/MediatecaCRM/ServletLink?METHOD=MEDIATECA&amp;accion=imagen&amp;id=3214" alt="De la tierra al mar" title="De la tierra al mar" style="width:95px" />
    </a>
    En este programa conocemos a Plácido, joven agricultor que nos mostrará la mala situación en que se encuentra el sector, informamos de la campaña 'Dale vida a tu árbol', asistimos a la presentación del libro 'Gestión ambiental. Guía fácil para empresas y profesionales', y nos hacemos eco del malestar de nuestros agricultores con la nueva normativa europea en materia de fitosanitarios, que entrará en vigor en junio de 2011.
    <a href="http://ficheros.7rm.es:3025/Video/3/2/3214_BAJA.mp4">
    <img src="/images/bajarArchivo.gif" alt="Descargar Archivo" title="Descargar Archivo" style="margin:0;padding:0 5px 0 0;vertical-align:middle;border:none" />
    </a>
    </dd>
    '''
    patron  = '<dt class="alacarta-video"><a href="([^"]+)" title="[^"]+">([^<]+)</a>.*?([0-9\/]+).*?</dt>[^<]+'
    patron += '<dd style="[^<]+">[^<]+'
    patron += '<a href="[^"]+" title="[^"]+">[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '</a>([^<]+)<a href="([^"]+)">'
    matches = re.compile(patron,re.DOTALL).findall(data)
    #scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        # Atributos del vídeo
        scrapedtitle = unicode( match[1].strip()+" ("+match[2]+")" , "iso-8859-1" , errors="ignore").encode("utf-8")
        scrapedurl = urlparse.urljoin(item.url,match[5]).replace("&amp;","&")
        scrapedthumbnail = urlparse.urljoin(item.url,match[3]).replace("&amp;","&")
        scrapedplot = unicode( match[4].strip()  , "iso-8859-1" , errors="ignore").encode("utf-8")
        scrapedpage = urlparse.urljoin(item.url,match[0]).replace("&amp;","&")
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], page=["+scrapedpage+"], thumbnail=["+scrapedthumbnail+"]")

        # Trata de sacar la fecha de emisión del título
        aired_date = scrapertools.parse_date(scrapedtitle)
        #logger.info("aired_date="+aired_date)

        # Añade al listado de XBMC
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , server="sieterm" , url=scrapedpage, thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot , show = item.show , page=scrapedpage, aired_date=aired_date, folder=False) )

    # Busca la página siguiente
    next_page_url = scrapertools.find_single_match(data,'<a class="list-siguientes" href="([^"]+)" title="Ver siguientes archivos">')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        next_page_item = Item(channel=CHANNELNAME, title=">> Página siguiente" , action="episodios" , url=next_page_url , show=item.show, folder=True)

        if load_all_pages:
            itemlist.extend(episodios(next_page_item,load_all_pages))
        else:
            itemlist.append( next_page_item )

    return itemlist

def detalle_episodio(item):

    #data = scrapertools.cache_page(item.url)

    item.geolocked = "0"

    try:
        from servers import sieterm as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def play(item):

    item.server="sieterm";
    itemlist = [item]

    return itemlist

# Test de canal
# Devuelve: Funciona (True/False) y Motivo en caso de que no funcione (String)
def test():
    
    # Carga el menu principal
    items_mainlist = mainlist(Item())

    # Busca un item con la lista de programas
    items_programas = []
    for item_mainlist in items_mainlist:

        if item_mainlist.action=="programas_antiguos":
            items_programas = programas_antiguos(item_mainlist)
            break

    if len(items_programas)==0:
        return False,"No hay programas antiguos"

    # Carga los episodios
    items_episodios = episodios(items_programas[0])
    if len(items_episodios)==0:
        return False,"No hay episodios en programa antiguo "+items_programas[0].title

    # Lee la URL del vídeo
    item_episodio = detalle_episodio(items_episodios[0])
    if item_episodio.media_url=="":
        return False,"El conector no devuelve enlace para el vídeo "+item_episodio.title


    # Busca un item con la lista de programas
    items_programas = []
    for item_mainlist in items_mainlist:

        if item_mainlist.action=="programas":
            items_programas = programas(item_mainlist)
            break

    if len(items_programas)==0:
        return False,"No hay programas nuevos"

    # Carga las temporadas
    items_temporadas = temporadas(items_programas[0])
    if len(items_temporadas)==0:
        return False,"No hay temporadas en programa nuevo "+items_programas[0].title
    
    # Carga los episodios
    items_episodios = videos(items_temporadas[0])
    if len(items_episodios)==0:
        return False,"No hay episodios en temporada "+items_temporadas[0].title+" de programa nuevo "+items_programas[0].title

    # Lee la URL del vídeo
    item_episodio = detalle_episodio(items_episodios[0])
    if item_episodio.media_url=="":
        return False,"El conector no devuelve enlace para el vídeo "+item_episodio.title

    return True,""
