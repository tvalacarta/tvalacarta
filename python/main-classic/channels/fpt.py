# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Fútbol Para Todos
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#
# Autor: Juan Pablo Candioti (@JPCandioti)
# Desarrollo basado sobre otros canales de tvalacarta
#------------------------------------------------------------

import urlparse,re
import urllib

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = True
CHANNELNAME = "fpt"
MAIN_URL = "http://www.futbolparatodos.com.ar"

def isGeneric():
    return True


def mainlist(item):
    logger.info("[" + CHANNELNAME + "] mainlist")

    # Descargo la página de la sección.
    item.url = MAIN_URL
    itemlist = []
    data = scrapertools.cachePage(item.url)
    data = scrapertools.find_single_match(data,"<h3>SECCIONES</h3>(.*?)</ul>")

    patron = '<li><img[^<]+<a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = ""
        plot = ""
        itemlist.append( Item(channel=CHANNELNAME, action="videos", title=title, thumbnail=thumbnail, plot=plot, url=url) )

    return itemlist


def videos(item):
    logger.info("[" + CHANNELNAME + "] videos")

    # Descargo la página de la sección.
    data = scrapertools.cachePage(item.url)
    if (DEBUG): logger.info(data)

    tipo = scrapertools.get_match(item.url, '/seccion/(.*?)')
    if tipo.endswith("/"):
        tipo = tipo[0:-1]

    try:
        pagina_siguiente = scrapertools.get_match(data, '<div\s+id="?(\d+)"?\s+class="ultimo removerultimo".*?>')
    except:
        pagina_siguiente = ""
    if (DEBUG): logger.info("pagina_siguiente=" + pagina_siguiente)

    # Extraigo id, imagen, título y descripción del video.
    '''
    <li class=golitem>
    <div style="position: relative;">
    <a href="http://www.youtube.com/embed/evylJotWAkU?autoplay=1" class="lbpModal cboxElement" title="El amor para toda la vida – Godoy Cruz – Fútbol Para Todos">
    <img src="http://img.youtube.com/vi/evylJotWAkU/0.jpg" width=210 alt="El amor para toda la vida – Godoy Cruz – Fútbol Para Todos"/>
    <img src="http://img.futbolparatodos.com.ar/wp-content/uploads/transparent-play-player2.png" width=210 style="position:absolute; z-index: 1; left: -1px;" alt=play class=transpa>
    </a>
    </div>
    <div class=golitemdetalle>14/03/2013</br> 
    <a href="http://www.futbolparatodos.com.ar/2013/03/14/el-amor-para-toda-la-vida-godoy-cruz-futbol-para-todos/">El amor para toda la vida – Godoy Cruz – Fútbol Para Todos</a>
    </br></div></li>
    '''
    patron  = '<li\s*class[^<]+'
    patron += '<div\s*style="position: relative[^<]+'
    patron += '<a\s*href="http://www.youtube.com/embed/(.{11})\?autoplay=1"[^<]+'
    patron += '<img\s*.*?src="([^"]+)"[^<]+'
    patron += '<img[^<]+'
    patron += '</a[^<]+'
    patron += '</div[^<]+'
    patron += '<div\s*class=golitemdetalle>[^<]+</br[^<]+'
    patron += '<a[^>]+>(.*?)</a></br>(.*?)</div></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    itemlist = []
    for id_video, ithumbnail, ititle, iplot in matches:
        ititle2 = re.sub(r"&#?\w+;", "", ititle)
        logger.info("[" + CHANNELNAME + "] title=" + ititle2)
        # Añado el item del video al listado.
        itemlist.append( Item(channel=CHANNELNAME, title=scrapertools.htmlclean(ititle2), action="play", server="youtube", url="http://www.youtube.com/watch?v="+id_video, thumbnail=ithumbnail, plot=iplot, folder=False) )

    # Si existe una página siguiente entonces agrego un item de paginación.
    if pagina_siguiente != "":
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente", action="videos", url=MAIN_URL+"/wp-content/themes/fpt2/jquery_cargar_videos.php?tipo="+tipo+"&desde="+str(int(pagina_siguiente)+1), folder=True) )

    return itemlist
