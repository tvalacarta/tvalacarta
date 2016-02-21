# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para tuteve
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import traceback

from core import logger
from core import config
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "tuteve"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.tuteve mainlist")

    item = Item(channel=CHANNELNAME, url="http://play.tuteve.tv")
    return secciones(item)

def secciones(item):
    logger.info("tvalacarta.channels.tuteve programas")
    itemlist = []

    '''
    <ul id="menuPrincipal" >
    <div class="container_12" id="listaMenu">
    <li class="item" href="#" style="display:none">Destacados</li>
    <li class="item" style="background-color:#000; color:#0477b6"><a href="/" style="background-color:#000; color:#0477b6; text-decoration:none">Se&ntilde;al en Vivo</a></li>
    <li class="item"><a href="http://play.tuteve.tv/canal/listado/todo/lo-ultimo" style="color:#6D7583; text-decoration:none">Lo &uacute;ltimo</a></li>
    <li class="item" onmouseout="verMenu('submenu_Novelas',0)" onmouseover="verMenu('submenu_Novelas',1)"> Novelas
    <div id="submenu_Novelas" class="submenu" style="width:403px; display:none; z-index:99">
    <div class="lista"> <a class="item" href="http://play.tuteve.tv/canal/programa/51784/avenida-peru">
    <div class="icoBullet"></div>
    <span class="titulo">Avenida Per&uacute;</span></a> <a class="item" href="http://play.tuteve.tv/canal/programa/51757/el-capo">
    '''

    # Extrae las series
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data,'<ul id="menuPrincipal"(.*?)</ul>')
    patron  = "<li class=\"item\" onmouseout=\"verMenu\('([^']+)',0\)\" onmouseover=\"verMenu\('[^']+',1\)\">([^<]+)<"
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    
    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.strip()
        title = scrapertools.htmlclean(title)
        thumbnail = ""
        plot = ""
        url = scrapedurl

        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="programas" , url=item.url , extra=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=True ) )

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.tuteve programas")
    itemlist = []

    '''
    <ul id="menuPrincipal" >
    <div class="container_12" id="listaMenu">
    <li class="item" href="#" style="display:none">Destacados</li>
    <li class="item" style="background-color:#000; color:#0477b6"><a href="/" style="background-color:#000; color:#0477b6; text-decoration:none">Se&ntilde;al en Vivo</a></li>
    <li class="item"><a href="http://play.tuteve.tv/canal/listado/todo/lo-ultimo" style="color:#6D7583; text-decoration:none">Lo &uacute;ltimo</a></li>
    <li class="item" onmouseout="verMenu('submenu_Novelas',0)" onmouseover="verMenu('submenu_Novelas',1)"> Novelas
    <div id="submenu_Novelas" class="submenu" style="width:403px; display:none; z-index:99">
    <div class="lista"> <a class="item" href="http://play.tuteve.tv/canal/programa/51784/avenida-peru">
    <div class="icoBullet"></div>
    <span class="titulo">Avenida Per&uacute;</span></a> <a class="item" href="http://play.tuteve.tv/canal/programa/51757/el-capo">
    '''
    '''
    <a class="item" href="http://play.tuteve.tv/canal/programa/51810/somos-empresa">
    <div class="icoBullet"></div>
    <span class="titulo">Somos Empresa</span></a> 
    '''

    # Extrae las series
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data,'<ul id="menuPrincipal"(.*?)</ul>')
    data = scrapertools.get_match(data,"<li class=\"item\" onmouseout=\"verMenu\('"+item.extra+"',0\)\" onmouseover=\"verMenu\('"+item.extra+"',1\)\">(.*?)</li")
    patron  = ' <a class="item" href="([^"]+)"[^<]+'
    patron += '<div class="icoBullet"></div[^<]+'
    patron += '<span class="titulo">([^<]+)</span></a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    
    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.strip()
        title = scrapertools.htmlclean(title)
        thumbnail = ""
        plot = ""
        url = scrapedurl+"/1"

        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="episodios" , url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=True ) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.tuteve episodios")
    itemlist=[]

    '''
    <div class="itmVideo" style="margin-right:0px; margin-left:20px;">
    <div class="imgCont">
    <a href="/videogaleria/programa/178856/2013-10-11-capitulo-102" id="itmVideo1">
    <img src="http://cdn.tuteve.tv/files/2013/10/11/316x202_Avenida.jpg" width="300" height="225" class="imgVideo" border="0" title="Avenida Perú - Capítulo 102" alt="Avenida Perú - Capítulo 102"/>
    </a></div>
    <div class="itmDesc">
    <div class="infoItem"> <span class="fechaItem">11.10.2013</span>
    <div class="vistasItem">
    <div class="icoVistas" style="float:left"></div>
    <span style="float:left"><b style="font-size:13px">10307</b> visitas</span> </div>
    </div>
    <div class="tituloItem">
    Avenida Perú                    <br />
    </div>
    <div class="titulocapitulo">Capítulo 102</div>
    <div class="introItem">María Fe revelará su mayor secreto frente a todos....</div>
    <div class="botonItem"><a href="/videogaleria/programa/178856/2013-10-11-capitulo-102">
    <div class="icoBullet"></div>
    <span class="botonTexto">VER VIDEO</span></a></div>
    </div>
    </div>
    '''
    # Extrae los episodios
    logger.info("item.url="+item.url)
    data = scrapertools.cachePage( item.url )
    logger.info("data=#"+data+"#")
    patron = '<div class="imgCont"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)"[^<]+</a[^<]+</div[^<]+'
    patron += '<div class="itmDesc".*?'
    patron += '<div class="tituloItem">([^<]+)<br[^<]+</div[^<]+'
    patron += '<div class="titulocapitulo">([^<]+)</div[^<]+'
    patron += '<div class="introItem">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle,episodio,scrapedplot in matches:
        title = scrapedtitle.strip()+" "+episodio
        title = scrapertools.htmlclean(title)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = scrapedplot
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="partes" , url=url , thumbnail=thumbnail , plot=plot , show=item.title , fanart=thumbnail , viewmode="movie_with_plot", folder=True ) )

    try:
        next_page=scrapertools.get_match(data,'<a class="botonNav" href="([^"]+)"[^<]+<div class="title">SIGUIENTE</div>')
        itemlist.append( Item( channel=item.channel , title=">> Página siguiente" , action="episodios" , url=urlparse.urljoin(item.url,next_page) ) )
    except:
        pass

    return itemlist

def partes(item):
    logger.info("tvalacarta.channels.tuteve partes")
    itemlist=[]

    # Extrae los episodios
    data = scrapertools.cachePage(item.url)
    try:
        data = scrapertools.get_match(data,'<ul id="mycarousel" class="jcarousel-skin-tango">(.*?)</ul>')
        patron = "<li>(.*?)</li>"
        matches = re.compile(patron,re.DOTALL).findall(data)
        scrapertools.printMatches(matches)

        for bloque in matches:
            title = scrapertools.find_single_match(bloque,'<div class="titulo"[^>]+>([^<]+)</div>').strip()
            thumbnail = scrapertools.find_single_match(bloque,'<img src="([^"]+)"')
            plot = scrapertools.find_single_match(bloque,"onclick=\"cargarVideoplayer\('([^']+)'")
            url = scrapertools.find_single_match(bloque,"onclick=\"cargarVideoplayer\('([^']+)'")
            if url.startswith("http://vk"):
                server = "vk"
            else:
                server = "youtube"

            itemlist.append( Item( channel=item.channel , title=title , action="play" , server=server , url=url , thumbnail=thumbnail , show=title , fanart=thumbnail , folder=False ) )
    except:
        logger.info(traceback.format_exc())

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    
    # El canal tiene estructura programas -> episodios -> play
    items_mainlist = mainlist(Item())
    items_programas = []

    # Todas las opciones del menu tienen que tener algo
    for item_mainlist in items_mainlist:
        exec "itemlist="+item_mainlist.action+"(item_mainlist)"
    
        if len(itemlist)==0:
            print "La sección '"+item_mainlist.title+"' no devuelve nada"
            return False

        items_programas = itemlist

    # Ahora recorre los programas hasta encontrar vídeos en alguno
    for item_programa in items_programas:
        print "Verificando "+item_programa.title
        items_episodios = episodios(item_programa)

        if len(items_episodios)>0:
            return True

    print "No hay videos en ningún programa"
    return False
