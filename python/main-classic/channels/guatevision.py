# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Guatevisión (Guatemala)
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
CHANNELNAME = "guatevision"
PROGRAMAS_URL = "http://guatevision.com/programas/"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.guatevision mainlist")

    return programas(Item(channel=CHANNELNAME))

def programas(item):
    logger.info("tvalacarta.channels.guatevision programas")

    itemlist = []

    if item.url=="":
        item.url=PROGRAMAS_URL

    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data,'<div class="main">(.*?)</div[^<]+</div')
    logger.info("tvalacarta.channels.guatevision data="+data)


    '''
    <a href="http://www.guatevision.com/programas/sinfiltro-lunes-a-viernes-22hrs/" title="Programas anteriores de #SinFiltro Lunes a Viernes 22hrs">
    <img width="300" height="100" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==" data-src="http://multimedia.guatevision.com/2016/01/identificador-sinfiltro300x100.jpg" class="enlaceprograma wp-post-image" alt="#SinFiltro Lunes a Viernes 22hrs" title="#SinFiltro Lunes a Viernes 22hrs"/>
    <noscript><img width="300" height="100" src="http://multimedia.guatevision.com/2016/01/identificador-sinfiltro300x100.jpg" class="enlaceprograma wp-post-image" alt="#SinFiltro Lunes a Viernes 22hrs" title="#SinFiltro Lunes a Viernes 22hrs"/></noscript></a>
    '''

    patron  = '<a href="([^"]+)"[^<]+'
    patron += '<img width="\d+" height="\d+" src="[^"]+" data-src="([^"]+)" class="[^"]+" alt="([^"]+)"[^<]+'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapedtitle.strip()
        thumbnail = scrapedthumbnail
        plot = ""
        url = scrapedurl
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
    logger.info("tvalacarta.channels.guatevision episodios")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    #logger.info("tvalacarta.channels.guatevision data="+data)

    '''
    <div class="video-wrapper">
    <a href="http://www.guatevision.com/playeryt.php?dedonde=yt_api3_menugtv.php&plid=PLGZsJXyG6Xyi173rWMMulkGeeuyMvknS-">
    <img src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==" data-src="https://i.ytimg.com/vi/xh-smylIaUU/mqdefault.jpg" border="0"/><noscript>
    <img src="https://i.ytimg.com/vi/xh-smylIaUU/mqdefault.jpg" border="0"/></noscript>
    <br>Programa 20/04/2016</a>
    </div>
    '''

    patron  = '<div class="video-wrapper"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img src="[^"]+" data-src="([^"]+)"[^<]+<noscript[^<]+'
    patron += '<img src="[^<]+</noscript[^<]+'
    patron += '<br>([^<]+)</a>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapedtitle.strip()
        thumbnail = scrapedthumbnail.replace("mqdefault","hqdefault")
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="playlist", url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail, viewmode="movie_with_plot", folder=True ) )

    '''
    <div class="video-wrapper">
    <a href="http://www.guatevision.com/playeryt.php?dedonde=yt_api3_sinreservasgtv.php&plid=PLd4wcfJeHB13ov0FrvnYrbuPNlmg3Kpl8">
    <img src="https://i.ytimg.com/vi/BId8bVVNaGA/mqdefault.jpg" border="0"/><br>Programa 16/05/2016</a>
    </div>
    '''
    patron  = '<div class="video-wrapper"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '<br>([^<]+)</a>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapedtitle.strip()
        thumbnail = scrapedthumbnail.replace("mqdefault","hqdefault")
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="playlist", url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail, viewmode="movie_with_plot", folder=True ) )

    return itemlist

def detalle_episodio(item):

    item.geolocked = "0"
    
    try:
        from servers import azteca13 as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def playlist(item):

    playlist_id = scrapertools.find_single_match(item.url,"plid=(.*?)$")

    import youtube_channel
    itemlist = youtube_channel.videos(Item(url=playlist_id))

    for item in itemlist:
        logger.info("tvalacarta.channels.guatevision item="+item.tostring())

    return itemlist

def play(item):

    item.server="guatevision";
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
