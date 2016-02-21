# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para upvtv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.upvtv get_video_url(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)
    media_url = scrapertools.find_single_match(data,'<video[^<]+<source.*?src="([^"]+)"')
    media_url = media_url.decode('iso-8859-1').encode("utf8","ignore")
    media_url = urllib.quote(media_url,":/")

    video_urls = []
    video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:] + " [upvtv]" , media_url ] )

    for video_url in video_urls:
        logger.info("tvalacarta.servers.upvtv %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve

