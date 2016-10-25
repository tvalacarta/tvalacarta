# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para 8TV
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

#import urlparse,urllib2,urllib,re
#import os
#from core import config

import re
from core import scrapertools
from core import logger
from core import jsontools

def get_video_url(page_url, premium = False, user="", password="", video_password="", page_data=""):

    logger.info("[vuittv.py] get_video_url(page_url='%s')" % page_url)

    video = []
    urlbase = "http://64.74.101.75:/services/mobile/streaming/index/master.m3u8?videoId=%s&pubId=%s"

    try:

        if page_url.startswith("rtmp://"):
            video.append([ "HTTP [mp4]", page_url])
        else:
            #
            # Busca url del video
            #
            # Ex: <iframe id="entry-player" src="//players.brightcove.net/1589608506001/78ec8cae-ae89-481a-8e95-b434e884e65c_default/index.html?videoId=5145516230001&autoplay"
            #
            data = scrapertools.downloadpage(page_url)
            data = data.replace("\\\"","")
            #logger.info("DATA: " + str(data))

            patron = '<iframe id="entry-player" src="([^"]+)"'
            matches = re.compile(patron,re.DOTALL).findall(data)
            #logger.info("MATCHES: " + str(matches))

            if len(matches) > 0:
                pat = 'players.brightcove.net/(\d+)/.*?/index.html\?videoId=(\d+)'
                mat = re.compile(pat,re.DOTALL).findall(matches[0])
                #logger.info("MAT: " + str(mat))
                url_final = urlbase % (mat[0][1], mat[0][0])
            else:
                url_final = ""

            video.append([ "HTTP [mp4]", url_final])

    except:
        import traceback
        logger.info(traceback.format_exc())

    return video
