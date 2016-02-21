# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para adnstream
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import re, sys
import urlparse, urllib, urllib2

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="" , video_password="" ):
    logger.info("[adnstream.py] get_video_url(page_url='%s')" % page_url)

    # Saca el código del vídeo
    if page_url.startswith("http://"):
        try:
            code = scrapertools.get_match(page_url,"http\://www.adnstream.com/video/([a-zA-Z]+)/")
        except:
            code = scrapertools.get_match(page_url,"http\://www.adnstream.tv/video/([a-zA-Z]+)/")
    else:
        code = page_url

    # Lee la playlist    
    url = "http://www.adnstream.com/get_playlist.php?lista=video&param="+code+"&c=463"
    data = scrapertools.cache_page(url)

    # Extrae la URL
    media_url = scrapertools.get_match(data,"<jwplayer:file>([^<]+)</jwplayer:file>")
    video_urls = [[ scrapertools.get_filename_from_url(media_url)[-4:] + ' [adnstream]' , media_url]]

    for video_url in video_urls:
        logger.info("[adnstream.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    logger.info("[adnstream.py] find_videos")

    encontrados = set()
    devuelve = []

    # http://www.adnstream.com/video/jvaRziGkoP/
    patronvideos  = 'adnstream.com/video/([a-zA-Z]+)'
    logger.info("[adnstream.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[adnstream]"

        url = "http://www.adnstream.com/video/"+match+"/"

        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'adnstream' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve

def test():

    video_urls = get_video_url("http://www.adnstream.com/video/jvaRziGkoP/")

    return len(video_urls)>0