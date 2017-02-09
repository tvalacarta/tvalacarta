# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Conector para telefe
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import jsontools

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.telefe get_video_url(page_url='%s')" % page_url)
    video_urls = []

    # Descarga la página del vídeo
    data = scrapertools.cache_page(page_url)
    data = scrapertools.find_single_match(data,'T3.content.cache = \{\s*"[^"]+"\:\s*(.*?)\}\;')
    logger.info("tvalacarta.servers.telefe videos data="+data)

    json_data = jsontools.load_json(data)

    for json_item in json_data["children"]["top"]["model"]["videos"][0]["sources"]:
        video_urls.append([ json_item["type"] , json_item["url"] ])

    for video_url in video_urls:
        logger.info("tvalacarta.servers.telefe %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # divxstage http://www.divxstage.net/video/2imiqn8w0w6dx"
    patronvideos  = 'http://www.divxstage.[\w]+/video/([\w]+)'
    logger.info("tvalacarta.servers.telefe find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[telefe]"
        url = "http://www.divxstage.net/video/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'divxstage' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
            
    return devuelve
