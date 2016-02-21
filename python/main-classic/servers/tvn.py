# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para tvn.cl
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os
import random

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("tvalacarta.servers.tvn get_video_url(page_url='%s')" % page_url)
    video_urls = []

    # Lee la página del vídeo
    data = scrapertools.cache_page(page_url)
    #url:'http://mdstrm.com/video/56be0bb3628451c3087f39b8.m3u8',
    media_url = scrapertools.find_single_match(data,"url\:'([^']+)'")
    video_urls.append( [ "m3u8 [tvn.cl]" , media_url ] )

    for video_url in video_urls:
        logger.info("tvalacarta.servers.tvn %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve

