# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para extremaduratv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.channels.extremaduratv get_video_url(page_url='%s')" % page_url)
    video_urls = []

    # Descarga la página como navegador web
    data = scrapertools.cache_page(page_url)

    '''
    <div 
    id="mediaplayer"
    data-vidUrl="rtmp://canalextremadura.cdn.canalextremadura.es/canalextremadura/tv/PROG00103641.mp4#535#300#/sites/default/files/los_ultimos_exclavos.jpg"
    data-iosUrl="http://iphonevod.canalextremadura.es/PROG00103641.mp4#535#300#/sites/default/files/los_ultimos_exclavos.jpg">
    </div>         
    '''

    # Descarga la página como ipad
    url = scrapertools.find_single_match(data,'data-iosUrl="([^\#]+)')
    logger.info("url="+url)
    video_urls.append( [ "para iOS (mp4) [extremaduratv]" , url[0:7]+urllib.quote(url[7:]) ] )

    #http://www.canalextremadura.es/alacarta/tv/videos/extremadura-desde-el-aire
    #<div id="mediaplayer" rel="rtmp://canalextremadurafs.fplive.net/canalextremadura/#tv/S-B5019-006.mp4#535#330"></div>
    url = scrapertools.find_single_match(data,'data-vidUrl="([^\#]+)')
    logger.info("url="+url)
    video_urls.append( [ "para Web (rtmp) [extremaduratv]" , url[0:7]+urllib.quote(url[7:]) ] )

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos  = '(http://www.canalextremadura.es/alacarta/tv/videos/([a-z0-9\-]+)'
    logger.info("tvalacarta.channels.extremaduratv find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[extremaduratv]"
        url = match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'tvg' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
            
    return devuelve

