# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para dwspan
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.dwspan get_video_url(page_url='%s')" % page_url)

    code = scrapertools.find_single_match(page_url,"/a(v-\d+)")

    data = scrapertools.cache_page("http://www.dw.com/html5Resource/"+code)
    media_url = data[1:-1]

    video_urls = []
    if media_url<>"":
        video_urls.append( [ "("+scrapertools.get_filename_from_url(media_url)[-4:]+") [dwspan]" , media_url ] )

    for video_url in video_urls:
        logger.info("tvalacarta.servers.dwspan %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
