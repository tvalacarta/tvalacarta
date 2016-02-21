# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para xiptv
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[xiptv.py] get_video_url(page_url='%s')" % page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)
    
    try:
        video_url = scrapertools.get_match(data,'src="([^"]+)" type="video/mp4"')
        video_urls.append( [ "mp4 [xiptv]" , video_url ] )
    except:
        # "url":"legacy/h264/20572","connection_url":"rtmp://cdn.xiptv.cat/vod"
        url = scrapertools.get_match(data,'"url"\:"([^"]+)"')
        logger.info("url="+url)
        connection_url = scrapertools.get_match(data,'"connection_url"\:"([^"]+)"')
        logger.info("connection_url="+connection_url)
        
        if url.startswith("/") or connection_url.endswith("/"):
            separador=""
        else:
            separador = "/"
        
        video_url = connection_url+separador+url+" playpath="+url
        
        video_urls.append( [ "rtmp [xiptv]" , video_url ] )

    for video_url in video_urls:
        logger.info("[xiptv.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve

