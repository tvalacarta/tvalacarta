# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para disney latino
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import jsontools

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("servers.disneylatino get_video_url(page_url='%s')" % page_url)
    video_urls = []

    #"bitrate":4138,"format":"mp4","id":"545a7c5d75d2a8495b000060","width":"1920","height":"1080","security_profile":["progressive","rtmpe","encrypted_hls"],"url":"http://media.disneyinternational.com/emea/kaltura/content/r71v1/entry/data/375/859/1_0cpytbx
    data = scrapertools.cache_page(page_url)
    patron = '"bitrate"\:(\d+),"format":"[^"]+","id":"[^"]+","width":"(\d+)","height":"(\d+)","security_profile":\[[^\]]+\],"url":"([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for calidad,ancho,alto,url in matches:
        video_urls.append( [ ancho+"x"+alto+" ("+calidad+"bps) [disneylatino]" , url ] )

    video_urls = sorted(video_urls, key=lambda item: int(scrapertools.find_single_match(item[0],"(\d+)")), reverse=True)

    for video_url in video_urls:
        logger.info("servers.disneylatino %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve

