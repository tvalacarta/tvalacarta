# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Intereconomia
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
CHANNELNAME = "intereconomia"
PROGRAMAS_URL = "http://www.intereconomia.tv/"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.intereconomia mainlist")

    return programas(Item(channel=CHANNELNAME))

def programas(item):
    logger.info("tvalacarta.channels.intereconomia programas")

    itemlist = []

    if item.url=="":
        item.url=PROGRAMAS_URL

    data = scrapertools.cache_page(item.url)

    patron  = '<div class="wpb_wrapper"[^<]+'
    patron += '<p[^<]+'
    patron += '<a href="([^"]+)" rel="attachment[^<]+'
    patron += '<img class="alignnone[^"]+" src="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail in matches:
        title = scrapedurl
        if title.startswith("/"):
            title = title[1:]
        title = title.replace("programas-completos","")
        title = title.replace("-"," ")
        title = title.capitalize().strip()

        thumbnail = scrapedthumbnail
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
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
    logger.info("tvalacarta.channels.intereconomia episodios")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    k = scrapertools.find_single_match(data,'<iframe id="HADOQ_iframe" src="http://hadoq.fractalmedia.es/embedcfgpl/([^\/]+)/')
    kparam = urllib.urlencode({"k":k})
    data = scrapertools.cache_page("https://hadoq.fractalmedia.es/rss/playlist.php?"+kparam+"&p=14&n=20")

    '''
    <item>
    <title><!\[CDATA\[El gato al agua | Parte 2 | 2017-01-16 23:02\]\]></title>
    <description><!\[CDATA\[El gato al agua | Parte 2 | 2017-01-16 23:02\]\]></description>
    <jwplayer:codigo>vmkYZbGnqH</jwplayer:codigo>
    <jwplayer:id>21730</jwplayer:id>
    <jwplayer:image>https://cdn035.fractalmedia.es/thumb/vmkYZbGnqH_w320.jpg</jwplayer:image>
    <jwplayer:source file='https://cdn038.fractalmedia.es/video/b4cc70f1b96da0152634292c8cba9dad/vmkYZbGnqH.H264-720p.mp4' />
    </item>        
    '''

    patron = '<item[^<]+'
    patron += '<title><!\[CDATA\[([^\]]+)\]\]></title[^<]+'
    patron += '<description><!\[CDATA\[([^\]]+)\]\]></description[^<]+'
    patron += '<jwplayer:codigo>[^<]+</jwplayer:codigo[^<]+'
    patron += '<jwplayer:id>[^<]+</jwplayer:id[^<]+'
    patron += '<jwplayer:image>([^<]+)</jwplayer:image[^<]+'
    patron += "<jwplayer:source file='([^']+)'"

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedtitle,scrapedplot,scrapedthumbnail,scrapedurl in matches:
        title = scrapedtitle.strip()
        thumbnail = scrapedthumbnail
        plot = scrapedplot
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="play", url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail, folder=False ) )

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
    return [item]

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
