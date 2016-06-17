# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para vtelevision
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

from core import scrapertools
from core import logger

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.vtelevision get_video_url page_url="+page_url)

    #<meta property="og:video" content="http://media.vtelevision.es/default/2011/06/17/0031_21_81405/Video/video_81405.mp4" />
    data = scrapertools.cache_page(page_url)
    media_url = scrapertools.find_single_match(data,'<meta property="og:video" content="([^"]+)"')

    video_urls = []
    video_urls.append([ scrapertools.get_filename_from_url(media_url)[-4:]+" [vtelevision]", media_url ])

    video_urls.reverse()

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
