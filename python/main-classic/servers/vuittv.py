# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para 8TV
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

#import urlparse,urllib2,urllib,re
#import os
#from core import config

import re,urllib2
from core import scrapertools
from core import logger
from core import jsontools

def get_video_url(page_url, premium = False, user="", password="", video_password="", page_data=""):

    logger.info("tvalacarta.servers.vuittv get_video_url page_url="+page_url)

    data = scrapertools.cache_page(page_url)
    url2 = scrapertools.find_single_match(data,'<iframe width="[^"]+" height="[^"]+" scrolling="[^"]+" data-src="(http://www-arucitys-com.filesusr.com[^"]+)"')
    logger.info("url2="+url2)

    data = scrapertools.cache_page(url2)
    media_url = scrapertools.find_single_match(data,'"sourceURL"\:"([^"]+)"')
    logger.info("media_url="+media_url)

    media_url = urllib2.unquote(media_url)
    logger.info("media_url="+media_url)
    
    video_urls = []
    video_urls.append([ scrapertools.get_filename_from_url(media_url)[-4:], media_url ])

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
