# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para sieterm
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("tvalacarta.servers.sieterm get_video_url(page_url='%s')" % page_url)
    
    data = scrapertools.cache_page(page_url)
    video_urls = []

    if page_url.startswith("xhttp"):
        video_urls.append( [ "mp4 [sieterm]" , page_url[1:] ] )

    else:
        player_url = scrapertools.find_single_match(data,'<script type="application/javascript" src="([^"]+)"')
        logger.info("tvalacarta.servers.sieterm player_url="+player_url)
        player_body = scrapertools.cache_page(player_url)
        #logger.info("tvalacarta.servers.sieterm player_body="+player_body)

        mediaurls = scrapertools.find_multiple_matches(player_body,'src\s*\:\s*"([^"]+)"')
        logger.info("tvalacarta.servers.sieterm mediaurls="+repr(mediaurls))

        for scrapedurl in mediaurls:

            mediaurl = scrapedurl

            if not mediaurl.startswith("http"):
                mediaurl = "http:"+scrapedurl

            logger.info("tvalacarta.servers.sieterm mediaurl="+mediaurl)

            if mediaurl.lower().endswith("m3u8"):
                title = "(m3u8)"
                video_urls.append( [ title , mediaurl ] )
            elif mediaurl.lower().endswith("mp4"):
                title = "(mp4)"
                video_urls.append( [ title , mediaurl ] )
            else:
                title = ""

    for video_url in video_urls:
        logger.info("tvalacarta.servers.sieterm %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []
            
    return devuelve

