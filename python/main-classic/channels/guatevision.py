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

    '''
    <div class="col-md-4">
    <div class="card card-raised card-background" style="background-image:url(http://s3-us-west-2.amazonaws.com/guatevision/wp-content/uploads/2016/10/05144725/TUTI-LANDING-WEB.jpg)">
    <div class="content">
    <h6 class="category text-info">Entretenimiento</h6>
    <a href="http://www.guatevision.com/programas/un-show-con-tuti/">
    <h4 class="card-title">Un Show con Tuti</h4>
    </a>
    <p class="card-description">Lunes a Viernes 8:00 PM</p>
    <a href="http://www.guatevision.com/programas/un-show-con-tuti/" class="btn btn-rose btn-round">
    <i class="material-icons">tv</i> &nbsp;VER
    </a>
    </div>
    </div>
    '''

    patron  = '<div class="col-md-4"[^<]+'
    patron += '<div class="card card-raised card-background" style="background-image.url\(([^\)]*)\)"[^<]+'
    patron += '<div class="content"[^<]+'
    patron += '<h6[^<]+</h6[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<h4 class="card-title">([^<]+)</h4'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedthumbnail,scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.strip()
        thumbnail = scrapedthumbnail
        plot = ""
        url = scrapedurl
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="episodios", url=url , thumbnail=thumbnail , plot=plot , show=title , view="programs", fanart=thumbnail ) )

    return itemlist

def detalle_programa(item):
    return item

def episodios(item):
    logger.info("tvalacarta.channels.guatevision episodios")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    #logger.info("tvalacarta.channels.guatevision data="+data)

    '''
    <div class="col-xs-12 col-sm-4 col-md-4">
    <div class = "card card-profile" style="background:#ffd131">   
    <div class = "card-image">       
    <a href = "#">           
    <img class = "img" src = "https://i.ytimg.com/vi/ueYFvacVTmo/hqdefault.jpg">       
    </a>       
    <div id="btn-playlist-6" class = "btn-playlist">               
    <i style="color:#FFFFFF;font-size:46px;" class="material-icons">play_circle_outline
    </i>       
    </div>   
    </div>   
    <div class = "content_title">       
    <h4  class = "card-title" style="height:50px;color:#434343">Programa 1 Temporada 2016
    </h4>   
    </div>
    </div>
    </div>
    <div style="clear:both;">
    </div>
    <div id="items-playlist-6" >
    <input type="hidden" class="titlelist" value="Programa 1 Temporada 2016" />
    <input type="hidden" class="vlist" value="ueYFvacVTmo" />
    <input type="hidden" class="vlist" value="iuFC6cpD8Xg" />
    <input type="hidden" class="vlist" value="z_wTFBrqWM0" /></div>
    '''

    patron  = '<div id="items-playlist[^<]+'
    patron += '<input type="hidden" class="titlelist" value="([^"]+)"(.*?)</div>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedtitle,extra in matches:
        title = scrapedtitle.strip()
        thumbnail = ""
        url = item.url+"?ep="
        plot = ""

        url_matches = re.compile('<input type="hidden" class="vlist" value="([^"]+)"',re.DOTALL).findall(extra)
        for url_match in url_matches:

            if thumbnail=="":
                thumbnail = "https://i.ytimg.com/vi/"+url_match+"/hqdefault.jpg"

            url = url + url_match + "|"

        url = url[:-1]
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="playlist", url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail, view="videos", folder=True ) )

    return itemlist

def detalle_episodio(item):
    return item

def playlist(item):
    logger.info("tvalacarta.channels.guatevision episodios")
    itemlist = []

    #http://www.guatevision.com/programas/bienes-inmuebles/?ep=e0NtgpW7Yng|kjWRm-zxU98|x1r_RLZkdi4|
    episode_codes_string = scrapertools.find_single_match(item.url,"ep=(.*?)$")
    logger.info("tvalacarta.channels.guatevision episode_codes_string="+episode_codes_string)
    episode_codes_list = episode_codes_string.split("|")

    i=1
    for episode_code in episode_codes_list:
        itemlist.append( Item( channel=item.channel , title=item.title+" (parte "+str(i)+")" , action="play", server="youtube", url="https://www.youtube.com/watch?v="+episode_code , thumbnail="https://i.ytimg.com/vi/"+episode_code+"/hqdefault.jpg" , show=item.show , view="videos", folder=False ) )
        i=i+1

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
