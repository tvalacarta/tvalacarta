# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para descargavideos
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("tvalacarta.servers.descargavideos get_video_url(page_url='%s')" % page_url)

    param = urllib.urlencode({"web":page_url})
    data = scrapertools.cache_page("http://www.descargavideos.tv/?"+param)
    #logger.info("data="+data)
    url = scrapertools.get_match(data,'href="/player/\?img\=[^\&]+&ext=[^\&]+&video=([^"]+)"')
    url = urllib.unquote(url)

    video_urls = []
    video_urls.append( [ "["+get_real_server_name(page_url)+"]" , url ] )

    for video_url in video_urls:
        logger.info("tvalacarta.servers.descargavideos %s - %s" % (video_url[0],video_url[1]))

    return video_urls

def get_real_server_name(page_url):

    real_server_name = "descargavideos"

    if "rtve.es" in page_url:
        real_server_name = "rtve"

    return real_server_name

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
