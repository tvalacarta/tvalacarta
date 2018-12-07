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

    '''
            <video id="5c04f64ee88f4"
               data-video-id="5971764264001"
               data-account="104403117001"
               data-player="SkevQBitbl"
               data-embed="default"
               class="video-js"
               controls></video>
    '''

    #http://players.brightcove.net/104403117001/SkevQBitbl_default/index.html?videoId=5971764264001

    data = scrapertools.cache_page(page_url)
    account = scrapertools.find_single_match(data,'data-account="([^"]+)"')
    logger.info("account="+account)
    player = scrapertools.find_single_match(data,'data-player="([^"]+)"')
    logger.info("player="+account)
    video_id = scrapertools.find_single_match(data,'data-video-id="([^"]+)"')
    logger.info("video_id="+video_id)

    api_url = "http://players.brightcove.net/"+account+"/"+player+"_default/index.html?videoId="+video_id

    ydl = youtube_dl.YoutubeDL({'outtmpl': u'%(id)s%(ext)s'})
    result = ydl.extract_info(api_url, download=False)
    logger.info("tvalacarta.servers.telemadrid get_video_url result="+repr(result))

    video_urls = []

    if "ext" in result and "url" in result:
        video_urls.append(["(.m3u8)", scrapertools.safe_unicode(result['url']).encode('utf-8')])
    else:

        if "entries" in result:
            for entry in result["entries"]:
                video_urls.append(["(.m3u8)", scrapertools.safe_unicode(entry['url']).encode('utf-8')])


    for video_url in video_urls:
        logger.info("tvalacarta.servers.telemadrid %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
