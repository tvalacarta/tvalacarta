# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para telemadrid
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("tvalacarta.servers.telemadrid get_video_url(page_url='%s')" % page_url)

    param = urllib.urlencode({"web":page_url})
    data = scrapertools.cache_page("http://www.descargavideos.tv/?"+param)
    logger.info("data="+data)
    url = scrapertools.get_match(data,'<input type="hidden" id="id1TVURL" name="video" value="([^"]+)">')

    video_urls = []
    video_urls.append( [ "[telemadrid]" , url ] )

    for video_url in video_urls:
        logger.info("[telemadrid.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
