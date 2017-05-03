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
    logger.info("tvalacarta.servers.telemadrid get_video_url(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)

    iframe = scrapertools.find_single_match(data,'<iframe id="miVideotm"[^<]+</iframe')
    media_url = scrapertools.find_single_match(iframe,'src="([^"]+)"')
    media_url = media_url+"http:"

    ydl = youtube_dl.YoutubeDL({'outtmpl': u'%(id)s%(ext)s'})
    result = ydl.extract_info(media_url, download=False)
    logger.info("tvalacarta.servers.telemadrid get_video_url result="+repr(result))

    video_urls = []

    if "ext" in result and "url" in result:
        video_urls.append(["[telemadrid]", scrapertools.safe_unicode(result['url']).encode('utf-8')])
    else:

        if "entries" in result:
            for entry in result["entries"]:
                video_urls.append(["[telemadrid]", scrapertools.safe_unicode(entry['url']).encode('utf-8')])


    for video_url in video_urls:
        logger.info("tvalacarta.servers.telemadrid %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
