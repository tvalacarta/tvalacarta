# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para euronews
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import jsontools

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.euronews get_video_url(page_url='%s')" % page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)
    json_data = scrapertools.find_single_match(data,'<div\s+id="jsMainMediaArticle"\s+class="media__video[^"]+"\s+data-content="([^"]+)"')
    logger.info("json_data0="+repr(json_data))

    from HTMLParser import HTMLParser
    h = HTMLParser()
    json_data = h.unescape(json_data)
    logger.info("json_data1="+repr(json_data))

    json_data = json_data.replace('\\','')
    logger.info("json_data2="+repr(json_data))

    #"videos":[{"format":"mp4","quality":"md","url":"http://video.euronews.com/mp4/med/EN/FU/SU/es/161017_FUSU_441B0-152919_S.mp4","editor":null,"duration":"249000","expiresAt":0},{"format":"mp4","quality":"hd","url":"http://video.euronews.com/mp4/EN/FU/SU/es/161017_FUSU_441B0-152916_S.mp4","editor":null,"duration":"249000","expiresAt":0}]
    json_data = scrapertools.find_single_match(json_data,'"videos"\:(\[.*?\])')
    logger.info("json_data="+repr(json_data))

    matches = re.findall('"quality"\:"([^"]+)"\,"url"\:"([^"]+)"',json_data,re.DOTALL)
    matches.reverse()
    for quality,media_url in matches:
        label = quality.upper()+" ["+scrapertools.get_filename_from_url(media_url)[-3:]+"] [euronews]"
        video_urls.append( [ label.encode("utf-8") , media_url ] )

    for video_url in video_urls:
        logger.info("tvalacarta.servers.euronews %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
