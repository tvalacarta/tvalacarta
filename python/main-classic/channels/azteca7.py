# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Azteca 7 (México)
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
CHANNELNAME = "azteca7"
PROGRAMAS_URL = "http://www.azteca7.com/"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.azteca7 mainlist")

    return programas(Item(channel=CHANNELNAME))

def programas(item):
    logger.info("tvalacarta.channels.azteca7 programas")

    itemlist = []

    if item.url=="":
        item.url=PROGRAMAS_URL

    data = scrapertools.cache_page(item.url)
    logger.info("tvalacarta.channels.azteca7 data="+data)

    '''
    <!-- MENU DEL SITIO -->
    <a href="javascript:" class="ztkTbAcTog"><i class="fa "></i>NUESTROS ESTRENOS<i class="fa fa-angle-down"></i></a><div class="ztkTbAcEl"><a href="http://www.azteca7.com/cocinerosmexicanos">Cocineros Mexicanos</a><a href="http://www.azteca7.com/despuesdetodo">Después de Todo</a>...<!-- FIN MENU DEL SITIO -->
    </div>
    '''
    data = scrapertools.find_single_match(data,'<!-- MENU DEL SITIO -->(.*?)<!-- FIN MENU DEL SITIO -->')

    patron = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.strip()
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        url = url+"/historico/videos"
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
    logger.info("tvalacarta.channels.azteca7 episodios")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    logger.info("tvalacarta.channels.azteca7 data="+data)

    '''
    <div>
    <a href="/videos/masalladelchisme/342702/sergio-mayer-nos-cuenta-sobre-como-se-siente-al-convertirse-en-abuelo">
    <img width="186" height="105" src="http://static.azteca.com/crop/crop.php?width=180&height=100&img=http://static.azteca.com/imagenes/2016/43/sergio-mayer,-mas-alla-del-chisme-2097468.jpg&coordinates=61,38">
    </a>
    <a href="/videos/masalladelchisme/342702/sergio-mayer-nos-cuenta-sobre-como-se-siente-al-convertirse-en-abuelo">
    <i class="icon-play-circle"></i>
    <h2 class="elemento_h2">Sergio Mayer nos cuenta sobre cómo se siente al convertirse en abuelo</h2></a>
    <h4>2016-10-28 17:00:00 hrs</h4>
    <p>Sergio Mayer nos cuenta sobre cómo se siente al convertirse en abuelo, además de contarnos de la abuela sexy que será Bárbara Mori</p>
    </div>
    '''

    patron  = '<div[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img width="\d+" height="\d+" src="([^"]+)"[^<]+'
    patron += '</a[^<]+'
    patron += '<a href="[^"]+"><i[^<]+</i><h2[^>]+>([^<]+)</h2></a[^<]+'
    patron += '<h4>([^<]+)</h4[^<]+'
    patron += '<p>([^<]+)</p'

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
    items_programas = mainlist(Item())

    if len(items_programas)==0:
        return False,"No hay programas"

    for item_programa in items_programas:
        items_episodios = episodios(item_programa)
        if len(items_episodios)>0:
            break

    if len(items_episodios)==0:
        return False,"No hay episodios"

    item_episodio = detalle_episodio(items_episodios[0])
    if item_episodio.media_url=="":
        return False,"El conector no devuelve enlace para el vídeo "+item_episodio.title

    return True,""
