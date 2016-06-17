# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para xip/tv
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib,re

from core import logger
from core import scrapertools
from core.item import Item 

DEBUG = False
CHANNELNAME = "xiptv"
PROGRAMAS_URL = "http://www.xiptv.cat/programes"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.xiptv mainlist")
    itemlist=[]
    itemlist.append( Item( channel=CHANNELNAME , title="Últimos vídeos añadidos"  , action="episodios" , url="http://www.xiptv.cat/capitols" , folder=True) )
    itemlist.append( Item( channel=CHANNELNAME , title="Televisiones locales"     , action="cadenas" , url="http://www.xiptv.cat" ))
    itemlist.append( Item( channel=CHANNELNAME , title="Todos los programas"      , action="programas" , url=PROGRAMAS_URL ))
    itemlist.append( Item( channel=CHANNELNAME , title="Programas por categorías" , action="categorias" , url="http://www.xiptv.cat/programes" ))
    return itemlist

def cadenas(item):
    logger.info("tvalacarta.channels.xiptv cadenas")
    itemlist=[]

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data,'<a href="#">Televisions locals</a>(.*?)</div>')

    # Extrae las categorias (carpetas)
    patron = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        url = scrapedurl
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="cadena" , url=url, folder=True) )

    return itemlist

def cadena(item):
    logger.info("tvalacarta.channels.xiptv cadena")
    itemlist=[]
    itemlist.append( Item( channel=CHANNELNAME , title="Últimos vídeos añadidos a "+item.title  , action="episodios" , url=urlparse.urljoin(item.url,"/capitols") , folder=True) )
    itemlist.append( Item( channel=CHANNELNAME , title="Todos los programas de "+item.title      , action="programas" , url=urlparse.urljoin(item.url,"/programes") ))
    return itemlist

def categorias(item):
    logger.info("tvalacarta.channels.xiptv categorias")
    itemlist=[]

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data,'<select id="program_program_categories" name="program.program_categories.">(.*?)</select>')

    # Extrae las categorias (carpetas)
    patron = '<option value="([^"]+)">([^>]+)</option>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle
        #http://www.xiptv.cat/programes?program%5Bfull_text%5D=&program%5Bprogram_categories%5D=Infantils&program%5Bhistoric%5D=1&commit=Cercar
        url = "http://www.xiptv.cat/programes?program%5Bfull_text%5D=&program%5Bprogram_categories%5D="+scrapedurl+"&program%5Bhistoric%5D=1&commit=Cercar"
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="programas" , url=url, folder=True) )

    return itemlist

def programas(item, load_all_pages=False):
    logger.info("tvalacarta.channels.xiptv programas")
    itemlist=[]

    if item.url=="":
        item.url=PROGRAMAS_URL
    
    # Extrae los programas
    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data,'(<li[^<]+<div class="item">.*?<div class="pager">.*?</div>)')
    '''
    <li>
    <div class="item">
    <div class="image drop-shadow curved curved-hz-1">
    <a href="/sex-toy-ficcions"><img alt="Frame_sex_toy_ficcions" src="/media/asset_publics/resources
    /000/106/321/program/FRAME_SEX_TOY_FICCIONS.JPG?1350386776" /></a>
    </div>
    <div class="archived"><em>Històric</em></div>
    <div class="content">
    <h4><a href="/sex-toy-ficcions">Sex Toy Ficcions</a></h4>
    <h5>
    <a href="/programes/page/10?model_type=Program&amp;program%5Bprogram_categories%5D=Nous+formats"
    >Nous formats</a>
    </h5>
    <p>Sèrie en clau de comèdia, que gira al voltant de reunions cada cop més habituals conegudes
    com a "tupper sex", trobades a domicili per millorar la vida sexual de les persones que hi participen
    . La intenció de Sex Toy Ficcions és aconseguir que l'espectador s'identifiqui amb les conductes i frustracions
    sexuals dels protagonistes d'aquesta ficció...</p>
    <span class="chapters">
    13 capítols
    </span>
    <dl>
    <dt>TV responsable</dt>
    <dd>La Xarxa</dd>
    <dt>Categoria</dt>
    <dd>
    <a href="/programes/page/10?model_type=Program&amp;program%5Bprogram_categories%5D=Nous+formats"
    >Nous formats</a>

    '''
    patron  = '<li>[^<]+<div class="item">(.*?)</li>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for match in matches:
        scrapedurl = scrapertools.find_single_match(match,'<a href="([^"]+)"')
        scrapedthumbnail = scrapertools.find_single_match(match,'<img alt="[^"]+" src="([^"]+)"')
        scrapedtitle = scrapertools.find_single_match(match,'<h4[^<]+<a href="[^"]+">([^<]+)</a>')
        scrapedcategory = scrapertools.find_single_match(match,'<h5[^<]+<a href="[^"]+">([^<]+)</a>')
        scrapedplot = scrapertools.find_single_match(match,'<p>(.*?)</p>')

        title = scrapertools.htmlclean(scrapedtitle)
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = scrapertools.htmlclean(scrapedcategory+"\n"+scrapedplot).strip()
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="episodios" , url=url, page=url , thumbnail=thumbnail, fanart=thumbnail, plot=plot , show=title , category = "programas" , viewmode="movie_with_plot", folder=True) )

    # Página siguiente
    next_page_url = scrapertools.find_single_match(data,'<a href="([^"]+)">next</a>')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        logger.info("next_page_url="+next_page_url)

        next_page_item = Item(channel=CHANNELNAME, title=">> Página siguiente" , action="programas" , extra="pager", url=next_page_url, folder=True)

        if load_all_pages:
            itemlist.extend(programas(next_page_item,load_all_pages))
        else:
            itemlist.append(next_page_item)

    return itemlist

def episodios(item):
    import urllib
    logger.info("tvalacarta.channels.xiptv episodios")
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    if item.url=="http://www.xiptv.cat/ben-trobats":
        data = scrapertools.find_single_match(data,'(<li[^<]+<div class="item">.*?<div class="pager">.*?</div>)',1)
    else:
        data = scrapertools.find_single_match(data,'(<li[^<]+<div class="item">.*?<div class="pager">.*?</div>)')
    '''
    <li>
    <div class="item">
    <div class="image drop-shadow curved curved-hz-1 ">
    <a href="/la-setmana-catalunya-central/capitol/capitol-30"><img alt="Imatge_pgm30" src="/media/asset_publics/resources/000/180/341/video/imatge_pgm30.jpg?1396620287" /></a>
    </div>
    <div class="content">
    <span class="date">
    04/04/2014
    </span>
    <h4>
    <a href="/la-setmana-catalunya-central/capitol/capitol-30">Capítol 30</a>
    </h4>
    <p><h5><a href="/la-setmana-catalunya-central" target="_blank">La setmana Catalunya central</a> </h5>
    </p>
    <span class="duration">25:02</span>
    <span class="views">0 reproduccions</span>
    <p>Al llarg dels segle XIX el Seminari de Vic va anar forjant una col·lecció de Ciències Naturals que representa, a dia d’avui, un valuós testimoni històric. Al programa d’avui coneixerem el nou destí de les peces que integren aquesta col·lecció i quin és el seu nou destí: integrar-se al fons del Museu del Ter de Manlleu. En aquesta edició de ‘La S...</p>
    <div class="related">
    '''
    patron = '<li[^<]+<div class="item">(.*?)<div class="related">'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for match in matches:
        fecha = scrapertools.find_single_match(match,'<span class="date">([^<]+)</span>').strip()
        duracion = scrapertools.find_single_match(match,'<span class="duration">([^<]+)</span>').strip()
        titulo_programa = scrapertools.find_single_match(match,'<p><h5><a[^>]+>([^<]+)</a>').strip()
        titulo_episodio = scrapertools.find_single_match(match,'<h4[^<]+<a[^>]+>([^<]+)</a>').strip()
        scrapedurl = scrapertools.find_single_match(match,'<h4[^<]+<a href="([^"]+)"')
        scrapedthumbnail = scrapertools.find_single_match(match,'<img alt="[^"]+" src="([^"]+)"')
        scrapedplot = scrapertools.find_single_match(match,'<p>([^<]+)</p>').strip()

        title = scrapertools.htmlclean(titulo_episodio) # + " (" + fecha + ") (" + duracion + ")")
        url = urlparse.urljoin( item.url , scrapedurl )
        thumbnail = urlparse.urljoin( item.url , scrapedthumbnail )
        plot = scrapertools.htmlclean(scrapedplot)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="play" , server="xiptv", url=url, thumbnail=thumbnail, fanart=thumbnail, plot=plot , show=item.show , category = item.category , viewmode="movie_with_plot", folder=False) )

    # Página siguiente
    patron = '<a href="([^"]+)">next</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for match in matches:
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , action="episodios" , extra="pager", url=urlparse.urljoin(item.url,match), show=item.show, folder=True) )

    return itemlist

def detalle_episodio(item):

    data = scrapertools.cache_page(item.url)

    scrapedplot = scrapertools.find_single_match(data,'<meta content="([^"]+)" property="og\:description"')
    item.plot = scrapertools.htmlclean( scrapedplot ).strip()

    scrapedthumbnail = scrapertools.find_single_match(data,'<meta content="([^"]+)" property="og\:image"')
    item.thumbnail = scrapedthumbnail.strip()

    scrapeddate = scrapertools.find_single_match(data,'<span class="date">([^<]+)</span>')
    item.aired_date = scrapertools.parse_date( scrapeddate.strip() )

    item.duration = scrapertools.find_single_match(data,'<span class="duration">([^<]+)</span>')

    item.geolocked = "0"
    
    try:
        from servers import xiptv as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def play(item):

    item.server="xiptv";
    itemlist = [item]

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    # Todas las opciones tienen que tener algo
    items = mainlist(Item())
    programas_items = programas(items[0])
    if len(programas_items)==0:
        return False

    episodios_items = episodios(programas_items[0])
    if len(episodios_items)==0:
        return False

    return bien
