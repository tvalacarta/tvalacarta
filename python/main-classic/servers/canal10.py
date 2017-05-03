# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para canal10
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import jsontools

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.canal10 get_video_url(page_url='%s')" % page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)
    iframe_url = scrapertools.find_single_match(data,'<iframe src="([^"]+)"')
    logger.info("iframe_url="+repr(iframe_url))

    headers = []
    headers.append(['User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'])
    headers.append(['Referer',page_url])
    data = scrapertools.cache_page(iframe_url, headers=headers)

    # Extrae las zonas de los programas
    patron = "src\:\s+'([^']+)',\s+type\:\s+'([^']+)'"
    matches = re.compile(patron,re.DOTALL).findall(data)

    for media_url,content_type in matches:
        video_urls.append( [ "("+scrapertools.get_filename_from_url(media_url)[-4:]+") [canal10]" , media_url ] )

    for video_url in video_urls:
        logger.info("tvalacarta.servers.canal10 %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
