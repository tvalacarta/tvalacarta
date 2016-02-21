# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Extremadura TV
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib,re

from core import logger
from core import scrapertools
from core.item import Item 

logger.info("[extremaduratv.py] init")

DEBUG = True
CHANNELNAME = "rtvv"
CHANNELCODE = "rtvv"

def isGeneric():
    return True

def mainlist(item):
    logger.info("[rtvv.py] mainlist")
    item.url = "http://www.rtvv.es/va/noualacarta/"
    itemlist = programas(item)
    return itemlist

def programas(item):
    logger.info("[rtvv.py] programas")
    itemlist=[]
    
    # Descarga la página
    data = scrapertools.cachePage(item.url)
    '''
    <div class="md-promo skin2 md">
    <div class="mg"><a href="/programa/10055/L-Alqueria_Blanca/capitulos.html" target="_self" title="Alqueria Blanca"><img alt="Alqueria Blanca" src="/bbtfile/5003_20110215PIjlzt.jpg" /></a></div>
    '''
    patron  = '<div class="md-promo skin2 md">[^<]+'
    patron += '<div class="mg"><a href="([^"]+)".*?title="([^"]+)"><img.*?src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for match in matches:
        scrapedtitle = match[1]
        scrapedurl = urlparse.urljoin(item.url,match[0])
        scrapedthumbnail = urlparse.urljoin(item.url,match[2])
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , category=scrapedtitle , show=scrapedtitle, page=scrapedurl) )

    return itemlist

def episodios(item):
    logger.info("[rtvv.py] episodios")

    itemlist = []

    # Extrae los videos
    data = scrapertools.cachePage(item.url)
    '''
    <div class="mg fl">
    <a title="Tornar al niu" href="/va/alqueriablanca/LAlqueria-Blanca-Tornar-niu-Cap_13_477082294.html">
    <img src="/alqueriablanca/LAlqueria-Blanca-Tornar-niu-Cap_RTVVID20110508_0069_3.jpg" width="145" height="109" alt="L&acute;Alqueria Blanca - Tornar al niu - Cap. 152" />
    </a>
    </div>    
    <div clasS="mt">
    <h3 class="title"><a href="/va/alqueriablanca/LAlqueria-Blanca-Tornar-niu-Cap_13_477082294.html">Cap. 152 - Tornar al niu</a></h3>
    <p class="section"><a href="/alqueriablanca/">L'Alqueria Blanca </a><span class="date">08.05.2011 / 22h14</span></p>
    <p class="body">
    Elena ix en llibertat, per&ograve; el pas pel calab&oacute;s deixa en ella una empremta profunda que la duu a prendre decisions dr&agrave;stiques. Don Mauro s&acute;enfronta al bisbe per defendre el seu suport a Elena i Robert. Sanitat tanca cautelarment la f&agrave;brica de calcer. Davant l&acute;actitud de Bali, &eacute;s Narc&iacute;s el qui mou els fils per tal que es re&ograve;briga. Jaume i Asun avancen la tornada i aix&ograve; porta Teresa a accelerar els preparatius de la boda.
    </p>
    '''
    patron  = '<div class="mg fl">[^<]+'
    patron += '<a[^>]+>[^<]+'
    patron += '<img src="([^"]+)"[^<]+>[^<]+'
    patron += '</a>[^<]+'
    patron += '</div>[^<]+'    
    patron += '<div clasS="mt">[^<]+'
    patron += '<h3 class="title"><a href="([^"]+)">([^<]+)</a></h3>[^<]+'
    patron += '<p class="section"><a[^>]+>[^<]+</a><span class="date">([^<]+)</span></p>[^<]+'
    patron += '<p class="body">([^<]+)</p>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for match in matches:
        scrapedtitle = match[2]+" ("+match[3]+")"
        scrapedurl = urlparse.urljoin(item.url,match[1])
        scrapedthumbnail = urlparse.urljoin(item.url,match[0])
        scrapedplot = match[4]
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , show=item.show , page=scrapedurl, category=item.category, folder=False) )

    patron  = '<div class="md-item">[^<]+'
    patron += '<div class="thumb-mediateca bspace6">[^<]+'
    patron += '<div class="mg">[^<]+'
    patron += '<a href="([^"]+)" title="([^"]+)">[^<]+'
    patron += '<img src="([^"]+)".*?'
    patron += '<var class="date">([^<]+)</var>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail,scrapedfecha in matches:
        title = scrapedtitle + " ("+scrapedfecha+")"
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="play" , url=url, thumbnail=thumbnail , show=item.show , page=url, category=item.category, folder=False) )

    patron = '<span class="next"><a.*?href="([^"]+)">Siguiente</a></span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)>0:
        logger.info("Página siguiente "+matches[0])
        itemlist.extend(episodios(Item(url=urlparse.urljoin(item.url,matches[0]),show=item.show)))
    
    patron = '<a class="ctrl ctrl-next[^"]+" href="([^"]+)" title="Anar a la p'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)>0:
        logger.info("Página siguiente "+matches[0])
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , action="episodios" , url=urlparse.urljoin(item.url,matches[0]), show=item.show) )
    
    return itemlist

def play(item):
    logger.info("[rtvv.py] play")

    url = item.url
    
    # Descarga pagina detalle
    #file: "/rtvvcontent/playlist/RTVVID20110207_0082/",
    #http://www.rtvv.es/rtvvcontent/playlist/RTVVID20110207_0082/
    data = scrapertools.cachePage(url)
    patron = 'file: "(/rtvvcontent/playlist/[^"]+)",'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)>0:
        url = urlparse.urljoin(url,matches[0])
    logger.info("[rtvv.py] url="+url)

    # Extrae la URL del video
    #<media:content url="http://rtvv.ondemand.flumotion.com/rtvv/ondemand/pro/RTVVID20110207_0082-0.mp4"/>
    data = scrapertools.cachePage(url)
    patron = '<media.content url="([^"]+)"/>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)>0:
        url = matches[0]

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title=item.title , action="play" , server="directo" , url=url, thumbnail=item.thumbnail, plot=item.plot , show=item.show , folder=False) )

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    programas_items = mainlist(Item())

    # Lista de programas
    if len(programas_items)==0:
        print "No hay programas"
        return False

    episodios_items = episodios(programas_items[0])
    if len(episodios_items)==0:
        print "El programa "+programas_items[0].title+" no tiene videos"
        return False

    mediaurl_items = play(episodios_items[0])
    if len(mediaurl_items)==0:
        print "Error al averiguar la URL del primer episodio de "+programas_items[0].title
        return False

    return True
