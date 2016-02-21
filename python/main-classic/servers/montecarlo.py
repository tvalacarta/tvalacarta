# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para Monte Carlo (Uruguay)
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.montecarlo get_video_url(page_url='%s')" % page_url)
    video_urls = []

    if page_data=="":
        data = scrapertools.cache_page(page_url)
    else:
        data = page_data

    media_url = scrapertools.find_single_match(data,'file\:\s*"([^"]+)"')
    logger.info("media_url="+media_url)
    video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:]+" [montecarlo]" , media_url ] )

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos  = '(montecarlotv.com.uy/programas/([^/]+)/videos/([^\"\/\']+)'
    logger.info("tvalacarta.servers.montecarlo find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[montecarlo]"
        url = match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'tvg' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
            
    return devuelve

