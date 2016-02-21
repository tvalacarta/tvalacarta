# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Extremadura TV
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "internautastv"

def isGeneric():
    return True

def mainlist(item):
    logger.info("[extremaduratv.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Ultimos videos"    , action="ultimosvideos" , url="http://www.internautas.tv/backend/mp4.xml") )
    itemlist.append( Item(channel=CHANNELNAME, title="Archivo"           , action="archivo"       , url="http://www.internautas.tv") )

    return itemlist

def ultimosvideos(item):
    logger.info("[internautastv.py] ultimosvideos")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    '''
    <item>
    <title>Polémicas declaraciones de Enrique Urbizu</title>
    <link>http://www.internautas.tv/programa/706.html</link>
    <description>No ha dejado a nadie indiferente las declaraciones del presidente de DAMA en la que le parece incluso que la polemica ley de los 3 avisos es insuficiente  </description>
    <enclosure url="http://serv2.internautas.tv/videos/m4v/20091229_1.m4v" type="video/m4v" />
    <pubDate>Tue, 29 Dec 2009 07:00:00 GMT</pubDate>
    <guid isPermaLink="true">http://www.internautas.tv/programa/706.html</guid>
    </item>
    '''
    patron  = '<item>[^<]+'
    patron += '<title>([^<]+)</title>[^<]+'
    patron += '<link>[^<]+</link>[^<]+'
    patron += '<description>([^<]+)</description>[^<]+'
    patron += '<enclosure url="([^"]+)"[^>]+>[^<]+'
    patron += '<pubDate>([^<]+)</pubDate>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        # Atributos del vídeo
        scrapedtitle = match[0].strip()+" ("+match[3].strip()+")"
        scrapedurl = urlparse.urljoin(item.url,match[2])
        scrapedthumbnail = ""
        scrapedplot = match[1].strip()
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=False) )

    return itemlist

def archivo(item):
    logger.info("[internautastv.py] archivo")

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    patron  = '<div class="barraopcion"><a href="([^"]+)">Archivo</a></div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    item.url = urlparse.urljoin(item.url,matches[0])

    return videosmes(item)

def videosmes(item):
    logger.info("[internautastv.py] videosmes")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    patron  = '<div class="cx7">([^<]+)<div class="ie"><a href="([^"]+)" title="([^"]+)" alt=""><img src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        # Atributos del vídeo
        scrapedtitle = "Día "+match[0]+" - "+match[2].strip()
        scrapedurl = urlparse.urljoin(item.url,match[1])
        scrapedthumbnail = urlparse.urljoin(item.url,match[3])
        scrapedplot = scrapedtitle
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="detail" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True) )

    # Busca los videos del mes
    patron  = '<div class="cx8">([^<]+)<div class="ie"><a href="([^"]+)" title="([^"]+)" alt=""><img src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        # Atributos del vídeo
        scrapedtitle = "Día "+match[0]+" - "+match[2].strip()
        scrapedurl = urlparse.urljoin(item.url,match[1])
        scrapedthumbnail = urlparse.urljoin(item.url,match[3])
        scrapedplot = scrapedtitle
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="detail" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True) )

    # Busca el enlace al mes anterior
    patron  = '<a href="([^"]+)">&lt;&lt;&lt;&nbsp;([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        # Atributos del vídeo
        scrapedtitle = "<< "+match[1].strip()
        scrapedurl = urlparse.urljoin(item.url,match[0])
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="videosmes" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True) )

    # Busca el enlace al mes siguiente
    patron  = '<a href="([^"]+)">([^\&]+)&nbsp;&gt;&gt;&gt;</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        # Atributos del vídeo
        scrapedtitle = ">> "+match[1].strip()
        scrapedurl = urlparse.urljoin(item.url,match[0])
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="videosmes" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True) )
    
    return itemlist

def detail(item):
    logger.info("[internautastv.py] detail")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    patron  = '<div class="c">.*?<span class="t2">([^<]+)</span>.*?'
    patron += '<div class="v1"><a href="([^"]+)"><img src="\/graficos\/lmp4\.jpg"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        # Atributos del vídeo
        scrapedtitle = item.title
        scrapedurl = match[1]
        scrapedthumbnail = item.thumbnail
        scrapedplot = match[0]
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=False) )

    return itemlist

def test():

    # Al entrar sale una lista de programas
    mainlist_items = mainlist(Item())
    videos_items = ultimosvideos(mainlist_items[0])
    if len(videos_items)==0:
        print "No devuelve últimos videos"
        return False

    return True