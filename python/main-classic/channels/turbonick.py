# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para 7rm
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,re
import urllib

from core import logger
from core import scrapertools
from core.item import Item

logger.info("[turbonick.py] init")

DEBUG = False
CHANNELNAME = "turbonick"

def isGeneric():
    return True

def mainlist(item):
    logger.info("[turbonick.py] mainlist")
    itemlist = []

    url = 'http://es.turbonick.nick.com/dynamo/turbonick/locale/common/xml/dyn/getGateways.jhtml'
    
    # --------------------------------------------------------
    # Descarga la página
    # --------------------------------------------------------
    data = scrapertools.cachePage(url)
    #logger.info(data)

    # --------------------------------------------------------
    # Extrae las categorias (carpetas)
    # --------------------------------------------------------
    patron = '<gateway cmsid="([^"]+)"\s+title="([^"]+)"\s+urlAlias="[^"]+"\s+iconurl="[^"]+"\s+iconurljpg="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG:
        scrapertools.printMatches(matches)

    for match in matches:
        scrapedtitle = match[1]
        scrapedurl = 'http://es.turbonick.nick.com/dynamo/turbonick/xml/dyn/getIntlGatewayByID.jhtml?id='+match[0]
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado de XBMC
        #addvideo( scrapedtitle , scrapedurl , category )
        if scrapedtitle=="EPISODIOS":
            itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="series" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , show=scrapedtitle , folder=True) )
        else:
            itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="videolist" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , show=scrapedtitle , folder=True) )

    return itemlist

def series(item):
    logger.info("[turbonick.py] series")
    itemlist = []

    # --------------------------------------------------------
    # Descarga la página
    # --------------------------------------------------------
    data = scrapertools.cachePage(item.url)
    #logger.info(data)

    # --------------------------------------------------------
    # Extrae los vídeos
    # --------------------------------------------------------
    patron  = '<content\s+cmsid="([^"]+)"\s+type="content"\s+contenttype="video"[^>]+>[^<]+<meta(.*?)</meta'
    bloques = re.compile(patron,re.DOTALL).findall(data)
    #if DEBUG: scrapertools.printMatches(bloques)
    
    dictionaryseries = {}
    
    for bloque in bloques:
        data = bloque[1]
        patron  = '<title>([^<]+)</title>[^<]+'
        patron += '<shorttitle>([^<]+)</shorttitle>[^<]+'
        patron += '<description>([^<]+)</description>.*?'
        patron += '<iconurl>([^<]+)</iconurl>[^<]+'
        patron += '<iconurljpg>([^<]+)</iconurljpg>.*?'
        patron += '<date>([^<]+)</date>.*?'
        patron += '<showname>([^<]+)</showname>[^<]+'
        patron += '<shortshowname>([^<]+)</shortshowname>[^<]+'
        patron += '<showid>([^<]+)</showid>[^<]+'
        matches = re.compile(patron,re.DOTALL).findall(data)
        #if DEBUG: scrapertools.printMatches(matches)
        idserie = matches[0][6]
        #logger.info("[turbonick.py] idserie="+idserie)

        if not dictionaryseries.has_key(idserie):
            logger.info("Nueva serie %s" % idserie)
            
            scrapedtitle = scrapertools.entityunescape(idserie)
            if scrapedtitle=="false":
                scrapedtitle="Otros"
            
            itemlist.append( Item(channel=CHANNELNAME, title = scrapedtitle , extra=idserie , action="episodios" , url=item.url, thumbnail="", plot="" , show=scrapedtitle , category=item.category , folder=True) )

            dictionaryseries[idserie] = True

    return itemlist

def episodios(item):
    logger.info("[turbonick.py] episodios")
    print item.tostring()
    itemlist = []

    # --------------------------------------------------------
    # Descarga la página
    # --------------------------------------------------------
    data = scrapertools.cachePage(item.url)
    #logger.info(data)

    # --------------------------------------------------------
    # Extrae los vídeos
    # --------------------------------------------------------
    patron  = '<content\s+cmsid="([^"]+)"\s+type="content"\s+contenttype="video"[^>]+>[^<]+<meta(.*?)</meta'
    bloques = re.compile(patron,re.DOTALL).findall(data)
    #if DEBUG: scrapertools.printMatches(bloques)
    
    for bloque in bloques:
        data = bloque[1]
        patron  = '<title>([^<]+)</title>[^<]+'
        patron += '<shorttitle>([^<]+)</shorttitle>[^<]+'
        patron += '<description>([^<]+)</description>.*?'
        patron += '<iconurl>([^<]+)</iconurl>[^<]+'
        patron += '<iconurljpg>([^<]+)</iconurljpg>.*?'
        patron += '<date>([^<]+)</date>.*?'
        patron += '<showname>([^<]+)</showname>[^<]+'
        patron += '<shortshowname>([^<]+)</shortshowname>[^<]+'
        patron += '<showid>([^<]+)</showid>[^<]+'
        matches = re.compile(patron,re.DOTALL).findall(data)
        #if DEBUG: scrapertools.printMatches(matches)
        match = matches[0]
        
        idserie = match[6]
        if match[1] != "false":
            scrapedtitle = match[1]+" - "+match[2]
        else:
            scrapedtitle = idserie+" - "+match[2]
        scrapedtitle = scrapertools.entityunescape(scrapedtitle)
        if scrapedtitle.startswith("DRAKE AND JOSH"):
            scrapedtitle = scrapedtitle.replace("DRAKE AND JOSH","DRAKE & JOSH") 
        scrapedthumbnail = match[3]
        if scrapedthumbnail == "false":
            scrapedthumbnail = ""
        scrapedplot = match[5]
        scrapedurl = 'http://es.turbonick.nick.com/dynamo/turbonick/xml/dyn/flvgenPT.jhtml?vid='+bloque[0]+'&hiLoPref=hi'
        
        #logger.info("[turbonick.py] idserie="+idserie)

        if idserie==item.extra:
            itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , show=item.show , category = item.category , folder=False) )

    return itemlist

def videolist(item):
    logger.info("[turbonick.py] videolist")
    itemlist = []

    # --------------------------------------------------------
    # Descarga la página
    # --------------------------------------------------------
    data = scrapertools.cachePage(item.url)
    #logger.info(data)

    # --------------------------------------------------------
    # Extrae los vídeos
    # --------------------------------------------------------
    patron  = '<content.*?'
    patron += 'cmsid="([^"]+)"'
    patron += '(?:\s+iconurl="([^"]+)")?.*?'
    patron += '<title>([^<]+)</title>.*?'
    patron += '<description>([^<]+)</description>.*?'
    patron += '(?:<iconurl>([^<]+)</iconurl>)?'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG:
        scrapertools.printMatches(matches)

    dictionaryurl = {}

    for match in matches:
        try:
            scrapedtitle = unicode( match[2] + " - " + match[3], "utf-8" ).encode("iso-8859-1")
        except:
            scrapedtitle = match[2] + " - " + match[3]
        scrapedurl = 'http://es.turbonick.nick.com/dynamo/turbonick/xml/dyn/flvgenPT.jhtml?vid='+match[0]+'&hiLoPref=hi'
        scrapedthumbnail = match[1]
        if scrapedthumbnail == "":
            scrapedthumbnail = match[4]
        if scrapedthumbnail == "false":
            scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado de XBMC
        if dictionaryurl.has_key(scrapedurl):
            logger.info("repetido")
        else:
            itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , show=item.show , folder=False) )
            dictionaryurl[scrapedurl] = True

    return itemlist

# URL del capítulo: http://es.turbonick.nick.com/turbonick/?extvideoid=7881
def play(item):
    import xbmc
    import xbmcgui
    
    logger.info("[turbonick.py] play")

    # Abre dialogo
    dialogWait = xbmcgui.DialogProgress()
    dialogWait.create( 'Descargando datos del vídeo...', item.title )

    # --------------------------------------------------------
    # Descarga pagina detalle
    # --------------------------------------------------------
    data = scrapertools.cachePage(item.url)
    patron = '<src>([^<]+)</src>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    url = matches[0]
    #rtmp://cp35019.edgefcs.net/ondemand/mtviestor/_!/intlnick/es/AVATAR/AVATAR1A_OD_640.flv
    #DEBUG: Protocol : RTMP
    #DEBUG: Hostname : cp35019.edgefcs.net
    #DEBUG: Port     : 1935
    #DEBUG: Playpath : mtviestor/_!/intlnick/es/AVATAR/AVATAR1A_OD_640
    #DEBUG: tcUrl    : rtmp://cp35019.edgefcs.net:1935/ondemand
    #DEBUG: app      : ondemand
    #DEBUG: flashVer : LNX 9,0,124,0
    #DEBUG: live     : no
    #DEBUG: timeout  : 300 sec
    cabecera = url[:35]
    logger.info("cabecera="+cabecera)
    finplaypath = url.rfind(".")
    playpath = url[35:finplaypath]
    logger.info("playpath="+playpath)

    logger.info("url="+url)

    # Playlist vacia
    playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
    playlist.clear()

    # Crea la entrada y la añade al playlist
    url = cabecera
    listitem = xbmcgui.ListItem( item.title, iconImage="DefaultVideo.png", thumbnailImage=item.thumbnail )
    listitem.setProperty("SWFPlayer", "http://es.turbonick.nick.com/global/apps/broadband/swf/bb_flv_player.swf")
    #listitem.setProperty("Playpath","14314/plus/plustv/PO778395")
    listitem.setProperty("Playpath",playpath)
    listitem.setProperty("Hostname","cp35019.edgefcs.net")
    listitem.setProperty("Port","1935")
    #listitem.setProperty("tcUrl","rtmp://od.flash.plus.es/ondemand")
    listitem.setProperty("tcUrl",cabecera)
    listitem.setProperty("app","ondemand")
    listitem.setProperty("flashVer","LNX 9,0,124,0")
    #listitem.setProperty("pageUrl","LNX 9,0,124,0")
    
    listitem.setInfo( "video", { "Title": item.title, "Plot" : item.plot , "Studio" : CHANNELNAME , "Genre" : item.category } )
    playlist.add( url, listitem )

    # Cierra dialogo
    dialogWait.close()
    del dialogWait

    # Reproduce
    xbmcPlayer = xbmc.Player( xbmc.PLAYER_CORE_AUTO )
    xbmcPlayer.play(playlist)   

    return []