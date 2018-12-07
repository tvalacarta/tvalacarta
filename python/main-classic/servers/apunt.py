# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para apunt
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.apunt get_video_url(page_url='%s')" % page_url)
    video_urls = []

    '''
    https://apuntmedia.es/va/a-la-carta/series/la-vall/capitol-11-diners-porcs
    OO.ready(function() {window.pp = OO.Player.create('container_1513685577', 'A5Z29uZzE6Mxifnhj11KYu3-yHTNp9Tx', playerParam);});
    https://secure-cf-c.ooyala.com/A5Z29uZzE6Mxifnhj11KYu3-yHTNp9Tx/1/dash/1.mpd
    https://player.ooyala.com/player/all/JrZndyZzE6rGJ_pdqQDDnrhf4m-1MUzL.m3u8
    '''

    data = scrapertools.cache_page(page_url)
    id_video = scrapertools.find_single_match(data,"OO.ready\(function\(\) \{window.pp \= OO.Player.create\('[^']+', '([^']+)'")
    logger.info("id_video="+id_video)

    media_url = "https://player.ooyala.com/player/all/"+id_video+".m3u8"

    video_urls.append( [ "("+scrapertools.get_filename_from_url(media_url)[-4:]+")" , media_url ] )

    for video_url in video_urls:
        logger.info("tvalacarta.servers.apunt %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
