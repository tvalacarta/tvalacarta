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
    logger.info("tvalacarta.servers.telemadrid get_video_url(page_url='%s')" % page_url)

    param = urllib.urlencode({"web":page_url})
    data = scrapertools.cache_page("http://www.descargavideos.tv/?"+param)
    logger.info("data="+data)
    url = scrapertools.get_match(data,'<div class="rtmpdump" id="rtmpcode1">(.*?)</div>')

    '''
    rtmpdump 
    -r "rtmp://telemadrid1-bc-od-flashfs.fplive.net/telemadrid1-bc-od-flash/?videoId=2787737986001&lineUpId=&pubId=104403117001&playerId=111787372001&affiliateId=" 
    -y "mp4:rtmp_uds/104403117001/201408/951/104403117001_3720475811001_d41e24bb-57a5-45de-8278-04a10ecd6fb3.mp4?videoId=2787737986001&lineUpId=&pubId=104403117001&playerId=111787372001&affiliateId="
    '''
    url = url.replace("rtmpdump -r ","")
    url = url.replace(" -y "," playpath=")
    url = url.replace('"','')
    url = url.strip()

    video_urls = []
    video_urls.append( [ "[telemadrid]" , url ] )

    for video_url in video_urls:
        logger.info("[telemadrid.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
