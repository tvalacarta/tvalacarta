# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para acbtv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.acbtv get_video_url(page_url='%s')" % page_url)

    #http://www.eltrecetv.com.ar/los-%C3%BAnicos/los-%C3%BAnicos-2012/00052062/cap%C3%ADtulo-28-los-%C3%BAnicos
    data = scrapertools.cache_page(page_url)

    '''
    var video_mobile_urls = {"IPHONE": "http://deportes.orange.es/acbtv/GestionVideos/videos/lacb_57_12_104_zza_ron_16x9_LQ.mp4", "ANDROID": "http://deportes.orange.es/acbtv/GestionVideos/videos/lacb_57_12_104_zza_ron_16x9_LQ.mp4", "ANDROID_TABLE": "http://deportes.orange.es/acbtv/GestionVideos/videos/lacb_57_12_104_zza_ron_16x9_HQ.mp4", "IPAD": "http://deportes.orange.es/acbtv/GestionVideos/videos/lacb_57_12_104_zza_ron_16x9_HQ.mp4"};
    var video_urls = ["http://deportes.orange.es/acbtv/GestionVideos/videos/lacb_57_12_104_zza_ron_16x9.flv", "http://deportes.orange.es/acbtv/GestionVideos/videos/lacb_57_12_104_zza_ron_16x9.flv", "http://deportes.orange.es/acbtv/GestionVideos/videos/lacb_57_12_104_zza_ron_16x9.flv", "http://video.acb.com/lacb_57_12_104_zza_ron_16x9.flv", "http://video.acb.com/lacb_57_12_104_zza_ron_16x9.flv", "http://video.acb.com/lacb_57_12_104_zza_ron_16x9.flv", "http://video.acb.com/lacb_57_12_104_zza_ron_16x9.flv", "http://video.acb.com/lacb_57_12_104_zza_ron_16x9.flv", "http://video.acb.com/lacb_57_12_104_zza_ron_16x9.flv", "http://video.acb.com/lacb_57_12_104_zza_ron_16x9.flv"];
    '''

    encontrados = set()
    video_urls = []
    
    mobile_urls = scrapertools.get_match(data,"var video_mobile_urls \= \{(.*?)\}")
    patron = '"([^"]+)"\: "([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(mobile_urls)

    for device,url in matches:

        if url not in encontrados:
            video_urls.append( [ "para "+device+" [acbtv]" , url ] )
            encontrados.add(url)

    web_urls = scrapertools.get_match(data,"var video_urls \= \[(.*?)\]")

    patron = '"([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(web_urls)

    for url in matches:

        if url not in encontrados:
            video_urls.append( [ "para Web [acbtv]" , url ] )
            encontrados.add(url)

    for video_url in video_urls:
        logger.info("tvalacarta.servers.acbtv %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve

