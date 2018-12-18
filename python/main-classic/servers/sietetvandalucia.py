# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para sietetvandalucia
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

from core import logger
from core import scrapertools
from core import jsontools

import urllib

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.sietetvandalucia get_video_url(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)
    media_url = scrapertools.find_single_match(data,'<a class="enlace-social icon_download[^"]+" title="Descargar[^"]+" href="([^"]+)"')

    video_urls = []
    video_urls.append(["(.mp4)", media_url])

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
