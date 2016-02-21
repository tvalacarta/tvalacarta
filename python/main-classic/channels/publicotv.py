# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Público TV
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = True
CHANNELNAME = "publicotv"

def isGeneric():
    return True

def mainlist(item):
    logger.info("[publicotv.py] mainlist")
    itemlist=[]

    url = "http://video.publico.es"

    # --------------------------------------------------------
    # Descarga la página
    # --------------------------------------------------------
    data = scrapertools.cachePage(url)
    #logger.info(data)

    # --------------------------------------------------------
    # Extrae los programas
    # --------------------------------------------------------
    patron = '<option value="(.*?)">(.*?)</option>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for match in matches:
        scrapedtitle = match[1]
        try:
            scrapedtitle = unicode( scrapedtitle, "utf-8" ).encode("iso-8859-1")
        except:
            pass
        scrapedurl = match[0]
        
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("scraped title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"] plot=["+scrapedplot+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="videolist" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , folder=True) )

    return itemlist

def videolist(item):
    logger.info("[publicotv.py] videolist")
    itemlist=[]

    # --------------------------------------------------------
    # Descarga la página
    # --------------------------------------------------------
    data = scrapertools.cachePage(item.url)
    #logger.info(data)

    # Extrae los vídeos
    patron  = '<div class="video-overview a1">[^<]+'
    patron += '<a href="([^"]+)" title="Play">'
    patron += '<img.*?src="(.*?)".*?title="([^"]+)"[^>]+></a>\W*<h4></h4>\W*<p class="title">(.*?)</p>\W*<div class="video-info-line">\W*<p>(.*?)</p>\W*<p>(.*?)</p>\W*</div>\W*</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for match in matches:
        scrapedtitle = match[3] + " ("+match[5]+") ("+match[4]+")"
        scrapedurl = urlparse.urljoin(item.url,match[0])
        scrapedthumbnail = urlparse.urljoin(item.url,match[1])
        scrapedplot = scrapertools.entityunescape(match[2])
        
        seppos = scrapedplot.find("--")
        scrapedplot = scrapedplot[seppos+2:]
        
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , folder=False) )

    # Página siguiente
    patron  = '<a href="([^"]+)" title="Ir a la siguiente[^"]+">Siguiente \&raquo\;</a></div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    if len(matches)>0:
        match = matches[0]
    
        scrapedtitle = "Página siguiente"
        scrapedurl = urlparse.urljoin(item.url,match)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="videolist" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , folder=True) )

    return itemlist

def play(item):
    logger.info("[publicotv.py] play")
    itemlist=[]

    #http://video.publico.es/videos/9/54777/1/recent
    '''
    1) La URL de detalle que encuentra ese patrón de arriba es del tipo: http://video.publico.es/videos/9/51046/1/recent
    2) El código en negrita tienes que usarlo para invocar a otra URL que te dará la ubicación del vídeo: http://video.publico.es/videos/v_video/51046
    3) En la respuesta de esa URL tienes el vídeo, dentro de la cabecera "Location" que he resaltado en negrita.

    HTTP/1.1 302 Found
    Date: Mon, 09 Nov 2009 13:34:14 GMT
    Server: Apache/2.2.3 (Red Hat)
    X-Powered-By: PHP/5.1.6
    Location: http://mm.publico.es/files/flvs/51046.49118.flv
    Content-Encoding: gzip
    Vary: Accept-Encoding
    Content-Length: 26
    Keep-Alive: timeout=5, max=77
    Connection: Keep-Alive
    Content-Type: text/html; charset=utf-8
    '''
    patron = 'http\:\/\/video.publico.es\/videos\/[^\/]+/([^\/]+)/'
    matches = re.compile(patron,re.DOTALL).findall(item.url)
    if DEBUG: scrapertools.printMatches(matches)
    
    url = 'http://video.publico.es/videos/v_video/'+matches[0]
    logger.info("url="+url)
    
    url = scrapertools.getLocationHeaderFromResponse(url)

    itemlist.append( Item(channel=CHANNELNAME, title=item.title , server = "directo" , action="play" , url=url, thumbnail=item.thumbnail, folder=False) )

    return itemlist
