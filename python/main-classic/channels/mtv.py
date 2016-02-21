# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para MTV
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import logger
from core import config
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "mtv"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.mtv mainlist")

    item = Item(channel=CHANNELNAME, url="http://www.mtv.es/programas/ver/")
    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.mtv programas")
    itemlist = []

    '''
    <div class="row row140" >
    <div class="thumbcontainer thumb140">
    <a href="/programas/100-artistas-mas-sexis/" title="Los 100 artistas más sexis" class="thumblink" >
    <img class="thumbnail " src="http://mtv-es.mtvnimages.com/marquee/KYLIE_SEXY_1.jpg?width=140&amp;quality=0.91" alt="Los 100 artistas más sexis" />
    </a>
    '''

    # Extrae las series
    data = scrapertools.cachePage(item.url)
    patron  = '<div class="row row140"[^<]+'
    patron += '<div class="thumbcontainer thumb140"[^<]+'
    patron += '<a href="([^"]+)" title="([^"]+)"[^<]+'
    patron += '<img class="thumbnail " src="(http://mtv-es.mtvnimages.com/.*?)\?'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    
    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        title = scrapedtitle.strip()
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        #http://www.mtv.es/programas/destacados/alaska-y-mario/
        #http://www.mtv.es/programas/destacados/alaska-y-mario/episodios/
        url = urlparse.urljoin(url,"episodios")

        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="episodios" , url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=True ) )

    try:
        next_page=scrapertools.get_match(data,'<a href="([^"]+)"><span class="link">Pr')
        #/videos?prog=3798&#038;v=1&#038;pag=2
        itemlist.append( Item( channel=item.channel , title=">> Página siguiente" , action="programas" , url=urlparse.urljoin(item.url,next_page) ) )
    except:
        pass

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.mtv episodios")
    itemlist=[]

    '''
    <div  class="row row160" >
    <div class="thumbcontainer thumb160">
    <a href="/programas/geordie-shore-6-temporada/episodios/geordie-shore-6-extra/video/geordie-shore-material-extra-979143/" title="Geordie Shore promo temporada 6: ¡en Australia!" class="thumblink" >
    <img class="thumbnail " src="http://mtv-es.mtvnimages.com/img/imagenes/promo-gs-new.jpg?height=120&amp;quality=0.91" alt="Geordie Shore promo temporada 6: ¡en Australia!" />
    <span class="video"> </span>
    </a>
    </div>
    <div class="link-block">     
    <a href="/programas/geordie-shore-6-temporada/episodios/geordie-shore-6-extra/video/geordie-shore-material-extra-979143/" title="Geordie Shore promo temporada 6: ¡en Australia!" class="titlelink " >Geordie Shore promo temporada 6: ¡en Australia!</a></div>
    <p  class="video-description" >Scott y Holly... en su vídeo más íntimo </p>
    <p  class="morelink" ><a href="/programas/geordie-shore-6-temporada/episodios/geordie-shore-6-extra/">Descripción completa</a> </p>
    </div>
    '''
    # Extrae los episodios
    data = scrapertools.cachePage( item.url )
    #logger.info("data="+data)
    patron  = '<div\s+class="row row[^<]+'
    patron += '<div\s+class="thumbcontainer thumb[^<]+'
    patron += '<a href="([^"]+)" title="([^"]+)" class="thumblink"[^<]+'
    patron += '<img class="thumbnail " src="(http://mtv-es.mtvnimages.com/.*?)\?'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        title = scrapedtitle.strip()
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="partes" , url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=True ) )

    try:
        #<a href="/programas/destacados/alaska-y-mario/episodios?start_20=20"><span class="link">Próximo</span>
        next_page=scrapertools.get_match(data,'<a href="([^"]+)"><span class="link">Pr')
        #/videos?prog=3798&#038;v=1&#038;pag=2
        itemlist.append( Item( channel=item.channel , title=">> Página siguiente" , action="episodios" , url=urlparse.urljoin(item.url,next_page) ) )
    except:
        pass

    return itemlist

def partes(item):
    logger.info("tvalacarta.channels.mtv partes")
    itemlist=[]

    '''
    <div class="row row70 " >
    <div class="thumbcontainer thumb70">
    <a href="/programas/geordie-shore-6-temporada/episodios/geordie-shore-606/video/geordie-shore-ep-606-parte-2-de-4-986977/" title="Geordie Shore Ep. 606 |Parte 2 de 4|" class="thumblink" >
    <img class="thumbnail " src="http://mtv-es.mtvnimages.com/img/imagenes/gs606b.jpg?height=53&amp;quality=0.91" alt="Geordie Shore Ep. 606 |Parte 2 de 4|" />
    <span class="video"> </span>
    </a>
    </div>
    '''
    # Extrae los episodios
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data,'<\!-- SM4.0 -->(.*?)<\!-- SM4.0 -->')
    patron  = '<div class="row row[^<]+'
    patron += '<div class="thumbcontainer thumb[^<]+'
    patron += '<a href="([^"]+)" title="([^"]+)" class="thumblink"[^<]+'
    patron += '<img class="thumbnail " src="(http://mtv-es.mtvnimages.com/.*?)\?'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        title = scrapedtitle.strip()
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="play" , server="mtv" , url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=False ) )

    try:
        #<a href="/programas/destacados/alaska-y-mario/episodios?start_20=20"><span class="link">Próximo</span>
        next_page=scrapertools.get_match(data,'<a href="([^"]+)"><span class="link">Pr')
        #/videos?prog=3798&#038;v=1&#038;pag=2
        itemlist.append( Item( channel=item.channel , title=">> Página siguiente" , action="episodios" , url=urlparse.urljoin(item.url,next_page) ) )
    except:
        pass

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    
    # El canal tiene estructura
    items_mainlist = mainlist(Item())
    if len(items_mainlist)==0:
        print "No hay programas"
        return False

    # Ahora recorre los programas hasta encontrar vídeos en alguno
    for item_programa in items_mainlist:
        print "Verificando "+item_programa.title
        items_episodios = episodios(item_programa)

        if len(items_episodios)>0:
            return True

    print "No hay videos en ningún programa"
    return False
