# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para disney channel
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import jsontools

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("tvalacarta.servers.disneychannel get_video_url(page_url='%s')" % page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)
    embed_url = scrapertools.find_single_match(data,'<meta itemprop="embedURL" content="([^"]+)"')
    
    data = scrapertools.cache_page(embed_url)
    data = scrapertools.find_single_match(data,'<script type="text/javascript">Disney.EmbedVideo\=(.*?)\;</script>')

    data_json = jsontools.load_json(data)
    logger.info("tvalacarta.servers.disneychannel data_json="+repr(data_json))

    for flavor in data_json["video"]["flavors"]:
        media_url = flavor["url"]
        video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:]+" "+str(flavor["bitrate"])+"bps [disneychannel]" , media_url ] )

    for video_url in video_urls:
        logger.info("tvalacarta.servers.disneychannel %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos  = '(http://replay.disneychannel.es/[^/]+/.*?.html)'
    logger.info("tvalacarta.servers.disneychannel find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[disneychannel]"
        url = match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'disneychannel' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
            
    return devuelve

