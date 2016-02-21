# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Telecinco
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse, re

try:
    from core import logger
    from core import scrapertools
    from core.item import Item
except:
    # En Plex Media server lo anterior no funciona...
    from Code.core import logger
    from Code.core import scrapertools
    from Code.core.item import Item

logger.info("[telecinco.py] init")

DEBUG = True
CHANNELNAME = "telecinco"

def isGeneric():
    return True

def mainlist(item):
    logger.info("[telecinco.py] mainlist")

    itemlist = []
    
    # El primer nivel de menú es un listado por canales
    itemlist.append( Item(channel=CHANNELNAME, title="Series"    , action="series"    , thumbnail = "" , url="http://www.telecinco.es/indiceSite/indiceSite6.shtml",category="series"))
    itemlist.append( Item(channel=CHANNELNAME, title="Programas" , action="programas" , thumbnail = "" , url="http://www.telecinco.es/indiceSite/indiceSite1887.shtml", category="programas"))

    return itemlist

def programas(item):
    logger.info("[telecinco.py] programas")
    return programas_principales(item)

def series(item):
    logger.info("[telecinco.py] series")
    itemlist = programas_principales(item)
    itemlist.extend( programas_secundarios(item))
    return itemlist

def programas_principales(item):
    logger.info("[telecinco.py] programas_principales")
    
    itemlist = []
    data = scrapertools.cachePage(item.url)
    
    # Extrae los programas
    patron  = '<div class="temasprincipales">(.*?)</div>'
    matches = re.findall(patron,data,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    if len(matches)>0:
        subdata = matches[0]
    else:
        return itemlist

    patron  = '<li class="dot"><a title="([^"]*)".*?href="([^"]+)"><img.*?src="([^"]+)"'
    matches = re.findall(patron,subdata,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    # Crea una lista con las entradas
    for match in matches:
        scrapedtitle = scrapertools.unescape(match[0]).strip()
        scrapedurl = urlparse.urljoin(item.url,match[1])
        
        if scrapedurl == "http://www.mitele.telecinco.es/t5/estaticos/aida/":
            scrapedtitle="Aida"
            scrapedurl="http://www.telecinco.es/aida/indiceSite/indiceSite2639.shtml"
        elif scrapedurl == "http://www.telecinco.es/tvmovies/indiceSite/indiceSite2238.shtml":
            scrapedtitle="La duquesa"
        elif scrapedurl == "http://www.telecinco.es/becarios/":
            scrapedurl="http://www.telecinco.es/becarios/indiceSite/indiceSite2670.shtml"
        elif scrapedurl == "http://www.telecinco.es/sexoenchueca":
            scrapedurl = "http://www.telecinco.es/sexoenchueca/indiceSite/indiceSite818.shtml"
        elif scrapedurl == "http://www.telecinco.es/adoptaunfamoso":
            scrapedurl = ""
        elif scrapedurl == "http://www.telecinco.es/piratas/":
            scrapedurl = "http://www.telecinco.es/piratas/indiceSite/indiceSite3591.shtml"

        #becarios, aida, adoptaunfamoso,sexoenchueca,
        # TODO: aida está temporada por temporada... 
        # TODO: becarios está temporada por temporada... 
        
        if scrapedtitle.startswith("'"):
            scrapedtitle = scrapedtitle[1:]
        if scrapedtitle.endswith("'"):
            scrapedtitle = scrapedtitle[:-1]
        if len(scrapedtitle)==0:
            # Extrae un título de la URL del programa
            try:
                scrapedtitle = scrapedurl.split("/")[3]
            except:
                scrapedtitle = scrapedurl
        scrapedthumbnail = urlparse.urljoin(item.url,match[2])
        scrapedplot = ""
        scrapedextra = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        
        if scrapedurl!="":
            itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="videos" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra = scrapedextra, show=scrapedtitle, category = item.category) )

    return itemlist

def programas_secundarios(item):
    logger.info("[telecinco.py] programas_secundarios")
    
    itemlist = []
    data = scrapertools.cachePage(item.url)
    
    # Extrae más programas
    patron  = '<div class="temassecundarios">(.*?)</ul>'
    matches = re.findall(patron,data,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    if len(matches)>0:
        subdata = matches[0]
    else:
        return itemlist

    #'<div class="main_title"><h1 style="margin: 20px 0 12px;font-size:1.75em;">TV Movies</h1></div><ul><li class="dot"><a title="Vuelo IL8714" target="_self" href="http://www.telecinco.es/tvmovies/indiceSite/indiceSite2635.shtml">Vuelo IL8714</a></li>'
    patron  = '<li class="dot"><a title="([^"]*)".*?href="([^"]+)">([^<]+)</a></li>'
    matches = re.findall(patron,subdata,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    # Crea una lista con las entradas
    for match in matches:
        scrapedtitle = scrapertools.unescape(match[2]).strip()
        scrapedurl = urlparse.urljoin(item.url,match[1])
        scrapedthumbnail = ""
        scrapedplot = ""
        scrapedextra = ""

        if scrapedurl == "http://www.telecinco.es/tvmovies//indiceSite/indiceSite1993.shtml":
            scrapedurl = ""

        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        if scrapedurl!="":
            itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="videos" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra = scrapedextra, show=scrapedtitle, category = item.category) )

    return itemlist

def videos(item):
    logger.info("[telecinco.py] videos")
    
    itemlist = []
    data = scrapertools.cachePage(item.url)
    
    # Extrae los programas
    patron  = '<div class="temasprincipales">(.*?)</div>'
    matches = re.findall(patron,data,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    if len(matches)>0:
        subdata = matches[0]
    else:
        return itemlist

    patron  = '<li class="dot"><a title="([^"]*)".*?href="([^"]+)"><img.*?src="([^"]+)"'
    matches = re.findall(patron,subdata,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    # Crea una lista con las entradas
    for match in matches:
        scrapedtitle = scrapertools.unescape(match[0]).strip()
        scrapedurl = urlparse.urljoin(item.url,match[1])
        
        if len(scrapedtitle)==0:
            # Extrae un título de la URL del programa
            try:
                scrapedtitle = scrapedurl.split("/")[3]
            except:
                scrapedtitle = scrapedurl
        scrapedthumbnail = urlparse.urljoin(item.url,match[2])
        scrapedplot = ""
        scrapedextra = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , show=item.show, extra = scrapedextra, category = item.title, folder=False) )

    return itemlist

def play(item):
    logger.info("[telecinco.py] play url1="+item.url)

    itemlist = []

    # Lee la página del vídeo (suele tener muchos más videos y enlaces)
    #http://www.telecinco.es/angelodemonio/indiceSite/indiceSite3172.shtml
    data = scrapertools.cachePage(item.url)
    
    # Extrae el bloque
    patron  = '<div class="temasprincipales">(.*?)</div>'
    matches = re.findall(patron,data,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    if len(matches)>0:
        subdata = matches[0]
    else:
        return itemlist

    # Extrae el primer elemento (el episodio completo)
    patron  = '<li class="dot"><a title="([^"]*)".*?href="([^"]+)"><img.*?src="([^"]+)"'
    matches = re.findall(patron,subdata,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    if len(matches)>0:
        url = matches[0][1].strip()
    else:
        return itemlist
    
    logger.info("url2="+url)
    
    # Esta URL es la del player ya
    #http://www.telecinco.es/angelodemonio/VideoViewer/VideoViewer.shtml?videoURL=33465
    partes = url.split("=")
    code = partes[len(partes)-1]
    logger.info("code="+code)
    
    # Consulta el WS con los metadatos del vídeo
    #http://www.mitele.telecinco.es/services/tk.php?provider=level3&protohash=/CDN/videos/465/33465.mp4
    url = "http://www.mitele.telecinco.es/services/tk.php?provider=level3&protohash=/CDN/videos/"+code[-3:]+"/"+code+".mp4"
    logger.info("url3="+url)
    data = scrapertools.cachePage(url)
    logger.info("data="+data[:100].replace("\n","A").replace("\r","D"))

    # Este es ya el vídeo
    #http://storage.telecinco.es/CDN/videos/465/33465.mp4?vf=20110321124040&vu=20110321154240&h=0d67038567ac3f45ec62e

    itemlist = []
    scrapedurl = data
    itemlist.append( Item(channel=CHANNELNAME, title=item.title , action="play" , server="directo" , url=scrapedurl, thumbnail=item.thumbnail, plot=item.plot, show=item.show, category = item.category, folder=False) )

    return itemlist