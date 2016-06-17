# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para acbtv
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import scrapertools
from core import config
from core.item import Item

DEBUG = config.get_setting("debug")
CHANNELNAME = "acbtv"
MAIN_URL = "http://acbtv.acb.com/"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.acbtv.mainlist")
    item.view="thumbnails"
    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.acbtv.programas")
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(MAIN_URL)
    patron = '<a href="(http.//acbtv.acb.com/channel/[^"]+)" class="nombre" title="([^"]+)"><img alt="[^"]+" src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(MAIN_URL,scrapedurl)
        thumbnail = urlparse.urljoin(MAIN_URL,scrapedthumbnail)
        plot = ""
        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url,  thumbnail=thumbnail , action="episodios" , show = item.title , extra="0", folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.acbtv.episodios")

    itemlist = []

    # Descarga la página
    channel_id = scrapertools.get_match(item.url,"channel/(.+)$")
    logger.info("tvalacarta.channels.acbtv.episodios channel_id="+channel_id)
    
    channel_videos_url = "http://acbtv.acb.com/component/0/"+item.extra+"/first_block_second_part/"+channel_id
    logger.info("tvalacarta.channels.acbtv.episodios channel_videos_url="+channel_videos_url)

    data = scrapertools.cache_page(channel_videos_url)
    data = data.replace("\\u003E",">")
    data = data.replace("\\u003C","<")
    data = data.replace("\\n","")
    data = data.replace('\\"','"')
    #logger.info("tvalacarta.channels.data="+data)
    
    # Extrae videos
    '''
    <div class="videos02">            <div class="img">    <a href="/video/4946-lacb-20112012-liga_regular-32-286-cai_zaragoza_mantiene_vivo_el_sueno_del_playoff"><img alt="Lacb_56_32_286_zza_sev_m" src="/media/videos/4946/small/lacb_56_32_286_zza_sev_m.jpg?1335705251" /></a></div><div class="text">  29.04.2012  <div class="titulo">    <a href="/video/4946-lacb-20112012-liga_regular-32-286-cai_zaragoza_mantiene_vivo_el_sueno_del_playoff">CAI Zaragoza mantiene vivo el sue\u00f1o del Playoff</a>  </div></div>            </div>
    '''
    patron  = '<div class="videos02"[^<]+'
    patron += '<div class="img"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img alt="[^"]+" src="([^"]+)"[^<]+</a[^<]+</div[^<]+'
    patron += '<div class="text">([^<]+)<div class="titulo"[^<]+<a[^>]+>([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,fecha,scrapedtitle in matches:
        title = scrapedtitle.strip().encode("utf8")+" "+fecha
        
        title = title.replace("\\u00e1","á")
        title = title.replace("\\u00e9","é")
        title = title.replace("\\u00ed","í")
        title = title.replace("\\u00f3","ó")
        title = title.replace("\\u00fa","ú")
        title = title.replace("\\u00f1","ñ")

        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url,  thumbnail=thumbnail , action="play" , server="acbtv", show = item.title , folder=False) )

    next_extra = str(int(item.extra)+1)
    itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , url=item.url,  thumbnail=thumbnail , action="episodios" , extra = next_extra , folder=True) )

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    # El canal tiene estructura programas -> episodios -> play
    programas = mainlist(Item())
    
    # Con que algún programa tenga episodios se da por bueno el canal
    bien = False
    for programa in programas:
        exec "episodios = "+programa.action+"(programa)"
        if len(episodios)>0:
            bien = True
            break
    
    return bien
