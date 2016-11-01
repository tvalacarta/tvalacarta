# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para rtvcm
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import jsontools

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("tvalacarta.servers.rtvcm get_video_url(page_url='%s')" % page_url)

    video_urls = []

    idvideo = scrapertools.find_single_match(page_url,"(\d+)$")
    url = "http://api.rtvcm.webtv.flumotion.com/pods/"+idvideo+"?extended=true"
    data = scrapertools.cache_page(url)
    logger.info("data="+data)
    json_object = jsontools.load_json(data)

    mediaurl="http://ondemand.rtvcm.ondemand.flumotion.com/rtvcm/ondemand/video/mp4/med/"+json_object["name"]
    video_urls.append( [ "(med) mp4 [rtvcm]" , mediaurl ] )

    mediaurl="http://ondemand.rtvcm.ondemand.flumotion.com/rtvcm/ondemand/video/mp4/mobile/"+json_object["name"]
    video_urls.append( [ "(mobile) mp4 [rtvcm]" , mediaurl ] )

    mediaurl="http://ondemand.rtvcm.ondemand.flumotion.com/rtvcm/ondemand/video/mp4/mini/"+json_object["name"]
    video_urls.append( [ "(mini) mp4 [rtvcm]" , mediaurl ] )

    for video_url in video_urls:
        logger.info("tvalacarta.servers.rtvcm %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []
            
    return devuelve

