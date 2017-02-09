# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para aragontv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.aragontv get_video_url(page_url='%s')" % page_url)

    video_urls = []

    data = scrapertools.cache_page(page_url)
    media_url = scrapertools.find_single_match(data,'src: "([^"]+)"')

    if media_url != "":
        video_urls.append( [ "para Web (m3u8) [aragontv]" , media_url ] )

    for video_url in video_urls:
        logger.info("tvalacarta.servers.aragontv %s - %s" % (video_url[0],video_url[1]))

    return video_urls

def get_video_url_from_page(page_url):
    # Descarga la página
    data = scrapertools.cache_page(page_url)

    try:
        final = scrapertools.get_match(data,"url\:'(mp4\%3A[^']+)'")
        principio = scrapertools.get_match(data,"netConnectionUrl\: '([^']+)'")

        if urllib.unquote(principio).startswith("rtmp://aragon") or urllib.unquote(principio).startswith("rtmp://iasoft"):
            url = principio+"/"+final[9:]
        else:
            url = principio+"/"+final
        url = urllib.unquote(url)

        host = scrapertools.find_single_match(url,'(rtmp://[^/]+)')
        app = scrapertools.find_single_match(url,'rtmp://[^/]+/(.*?)/mp4\:')
        playpath = scrapertools.find_single_match(url,'rtmp://[^/]+/.*?/(mp4\:.*?)$')

        url = host+' app='+app+' playpath='+playpath

        logger.info("url="+url)
    except:
        url = ""
        logger.info("url NO encontrada")

    return url

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve

