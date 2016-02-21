# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para telemadrid
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("tvalacarta.servers.telemundo get_video_url(page_url='%s')" % page_url)

    video_urls = []
    '''
    linkHtml(
    'http://telemundo-pmd.edgesuite.net/MPX/video/NBCU_Telemundo/670/531/150108_2839125_El_hijo_del_sicario_y_muerte_segura__Caso_Ce_4000.mp4?hdnea=st=1421188135~exp=1421189335~acl=/*~hmac=e6d744871714b5f94945354189d241cca25d82ce',
    'Descargar en calidad 4000',
    '''
    param = urllib.urlencode({"web":page_url})
    data = scrapertools.cache_page("http://www.descargavideos.tv/?"+param)
    patron = "linkHtml\(\s+"
    patron += "'([^']+)',\s+"
    patron += "'([^']+)'"
    matches = re.compile(patron,re.DOTALL).findall(data)

    for url,title in matches:
        video_urls.append( [ title.replace("Descargar en calidad ","")+"bps [telemundo]" , url ] )

    for video_url in video_urls:
        logger.info("[telemadrid.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
