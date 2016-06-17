# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Azteca 13 (México)
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import config
from core import logger
from core import scrapertools
from core import jsontools
from core.item import Item

DEBUG = config.get_setting("debug")
CHANNELNAME = "azteca13"
PROGRAMAS_URL = "http://www.aztecatrece.com/"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.azteca13 mainlist")

    return programas(Item(channel=CHANNELNAME))

def programas(item):
    logger.info("tvalacarta.channels.azteca13 programas")

    itemlist = []

    if item.url=="":
        item.url=PROGRAMAS_URL

    data = scrapertools.cache_page(item.url)
    logger.info("tvalacarta.channels.azteca13 data="+data)
    data = scrapertools.find_single_match(data,'<span>Programas(.*?)<div class="col-md-4')

    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.strip()
        thumbnail = ""
        plot = ""
        url = "http://www.aztecatrece.com/"+scrapedurl+"/historico/capitulos"
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="episodios", url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail, view="videos" ) )

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.page)

    item.plot = scrapertools.find_single_match(data,'<article class="span8"[^<]+<div class="contenido_noticia">(.*?)</div>')
    item.plot = scrapertools.htmlclean(item.plot).strip()

    item.thumbnail = scrapertools.find_single_match(data,'<img src="([^"]+)" alt="" class="img-det-not">')

    #item.title = scrapertools.find_single_match(data,'<article class="span8"[^<]+<h2>([^<]+)</h2>')

    return item

def episodios(item):
    logger.info("tvalacarta.channels.azteca13 episodios")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    '''
    <div>
    <a href="/videos/escapeperfecto/302470/mira-nuestro-detras-de-camaras">
    <img width="186" height="105" src="http://static.azteca.com/crop/crop.php?width=180&height=100&img=http://static.azteca.com/imagenes/2016/05/2042193--mira-nuestro-detras-de-camaras-.jpg&coordinates=50,50">
    </a>
    <a href="/videos/escapeperfecto/302470/mira-nuestro-detras-de-camaras"><i class="icon-play-circle"></i>¡Mira nuestro detrás de cámaras!</a>
    <h4>2016-02-02 21:36:00 hrs</h4>
    <p>Conoce algunas cosas curiosas que pasan detrás de las cámaras de Escape Perfecto</p>
    </div>
    '''

    patron  = '<div[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img width="\d+" height="\d+" src="([^"]+)"[^<]+'
    patron += '</a[^<]+'
    patron += '<a href="[^"]+"><i[^<]+</i>([^<]+)</a[^<]+'
    patron += '<h4>([^<]+)</h4[^<]+'
    patron += '<p>([^<]+)</p>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle,fecha,scrapedplot in matches:
        title = scrapedtitle.strip()+" "+fecha.strip()
        thumbnail = scrapedthumbnail
        plot = scrapedplot
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="play", server="azteca", url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail, folder=False ) )

    return itemlist

def detalle_episodio(item):

    item.geolocked = "0"
    
    try:
        from servers import azteca as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def play(item):

    item.server="azteca";
    itemlist = [item]

    return itemlist

# Test de canal
# Devuelve: Funciona (True/False) y Motivo en caso de que no funcione (String)
def test():
    
    # Carga el menu principal
    items_mainlist = mainlist(Item())

    # Busca el item con la lista de programas
    items_programas = []
    for item_mainlist in items_mainlist:

        if item_mainlist.action=="programas":
            items_programas = programas(item_mainlist)
            break

    if len(items_programas)==0:
        return False,"No hay programas"

    # Carga los episodios
    items_episodios = episodios(items_programas[0])
    if len(items_episodios)==0:
        return False,"No hay episodios en "+items_programas[0].title

    # Lee la URL del vídeo
    item_episodio = detalle_episodio(items_episodios[0])
    if item_episodio.media_url=="":
        return False,"El conector no devuelve enlace para el vídeo "+item_episodio.title

    return True,""
