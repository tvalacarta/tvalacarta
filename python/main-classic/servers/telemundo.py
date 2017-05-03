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

from lib import youtube_dl

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("tvalacarta.servers.telemundo get_video_url page_url="+page_url)

    video_urls = []

    ydl = youtube_dl.YoutubeDL({'outtmpl': u'%(id)s%(ext)s'})
    result = ydl.extract_info(page_url, download=False)
    logger.info("tvalacarta.servers.telemadrid get_video_url result="+repr(result))

    video_urls = []

    if "ext" in result and "url" in result:
        video_urls.append(["[telemundo]", scrapertools.safe_unicode(result['url']).encode('utf-8')])
    else:

        if "entries" in result:
            for entry in result["entries"]:
                video_urls.append(["[telemundo]", scrapertools.safe_unicode(entry['url']).encode('utf-8')])

    for video_url in video_urls:
        logger.info("tvalacarta.servers.telemundo %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
