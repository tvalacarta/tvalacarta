# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para trececl
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import jsontools

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.trececl get_video_url(page_url='%s')" % page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)
    media_url = scrapertools.find_single_match(data,'var\s*articuloVideo\s*\=\s*"([^"]+)"')
    logger.info("media_url="+repr(media_url))

    video_urls.append( [ "("+scrapertools.get_filename_from_url(media_url)[-4:]+") [trececl]" , media_url ] )

    for video_url in video_urls:
        logger.info("tvalacarta.servers.trececl %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
