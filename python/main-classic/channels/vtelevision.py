# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para V Televisión (Galicia)
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
CHANNELNAME = "vtelevision"
PROGRAMAS_URL = "http://www.vtelevision.es/programas/index.htm"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.vtelevision mainlist")

    return programas(Item(channel=CHANNELNAME))

def programas(item):
    logger.info("tvalacarta.channels.vtelevision programas")

    itemlist = []

    if item.url=="":
        item.url=PROGRAMAS_URL

    data = scrapertools.cache_page(item.url)
    logger.info("tvalacarta.channels.vtelevision data="+data)
    data = scrapertools.find_single_match(data,'<option select="selected">Selecciona Programa</option>(.*?)</select>')

    patron = '<option value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:

        title = unicode(scrapedtitle,"iso-8859-1").encode("utf-8")
        title = title.replace("«","")
        title = title.replace("»","")
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="episodios", url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail ) )

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.page)

    item.plot = scrapertools.find_single_match(data,'<article class="span8"[^<]+<div class="contenido_noticia">(.*?)</div>')
    item.plot = scrapertools.htmlclean(item.plot).strip()

    item.thumbnail = scrapertools.find_single_match(data,'<img src="([^"]+)" alt="" class="img-det-not">')

    #item.title = scrapertools.find_single_match(data,'<article class="span8"[^<]+<h2>([^<]+)</h2>')

    return item

def episodios(item):
    logger.info("tvalacarta.channels.vtelevision episodios")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    #rss('ext', '/estaticos/caja_ultimos_sobresaintes.htm'
    url = scrapertools.find_single_match(data,"rss.'ext', '([^']+)'")
    data = scrapertools.cache_page( urlparse.urljoin(item.url,url) )
    '''
    <div class="vid">
    <a href="/programas/sobresaintes/2011/06/17/0031_21_81405.htm">
    <img alt="Â«SobresaÃ­ntesÂ» Os chistes e as adiviÃ±as dos mÃ¡is pequenos (cap.65-17/06)" src="http
    ://media.vtelevision.es/scale.php?w=150&i=/default/2011/06/17/0031_21_81405/Foto/img_81405.jpg" />
    </a>
    <div class="text">
    <em>
    <strong>&nbsp;</strong>
    Sobresaintes
    </em>
    <small id="fecha01011331535861198576943_0031_21_81405">&nbsp;</small>
    <script language="javascript">pintaFecha("fecha01011331535861198576943_0031_21_81405", 1308265204000
    , 1308265204000);</script>
    <h2 id="titulo01011331535861198576943_0031_21_81405">
    <a href="/programas/sobresaintes/2011/06/17/0031_21_81405.htm">Â«SobresaÃ­ntesÂ» Os chistes e as
    adiviÃ±as dos mÃ¡is pequenos (cap.65-17/06)</a>
    </h2>
    '''

    patron  = '<div class="vid"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img alt="([^"]+)" src="([^"]+)"[^<]+'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        title = scrapedtitle.strip()
        thumbnail = scrapedthumbnail
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="play", server="vtelevision", url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail, folder=False ) )

    return itemlist

def detalle_episodio(item):

    item.geolocked = "0"
    
    try:
        from servers import vtelevision as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def play(item):

    item.server="vtelevision";
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
