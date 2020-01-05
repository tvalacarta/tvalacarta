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
from core import jsontools

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.extremadura get_video_url(page_url='%s')" % page_url)
    video_urls = []

    #<iframe src="https://cdnapi.shooowit.net/vdmplayer/8849c4d9-1234-41eb-99bb-094f88b30a94"
    #https://cdnapi.shooowit.net/apicloud/v1.0/public/iframe/8849c4d9-1234-41eb-99bb-094f88b30a94
    #{"id":"8849c4d9-1234-41eb-99bb-094f88b30a94","name":"auto-publication PROG00184235.mp4","activ...
    #"m3u8":"//stgcdnvod.shooowit.net/ondemand/2f89ac25-ad8f-4d56-a6e2-3fc953c9a076/430cc7be-7aa3-43e6-8482-45e224930d33_Fast_H,300,600,1500,.mp4.m3u8",
    #"progressive":"//storagecdn.shooowit.net/ondemand/2f89ac25-ad8f-4d56-a6e2-3fc953c9a076/430cc7be-7aa3-43e6-8482-45e224930d33_Fast_H1500.mp4"}

    data = scrapertools.cache_page(page_url)
    video_code = scrapertools.find_single_match(data,'iframe src="https://cdnapi.shooowit.net/vdmplayer/([a-f\-\d+]+)"')
    logger.info("tvalacarta.servers.extremadura video_code="+repr(video_code))

    # Videos actuales
    if video_code:
        json_url = "https://cdnapi.shooowit.net/apicloud/v1.0/public/iframe/"+video_code
        json_data = jsontools.load_json(scrapertools.cache_page(json_url))

        media_url = "http:"+json_data["media"]["m3u8"]
        logger.info("media_url="+repr(media_url))
        video_urls.append( [ "("+scrapertools.get_filename_from_url(media_url)[-5:]+")" , media_url ] )

        media_url = "http:"+json_data["media"]["progressive"]
        logger.info("media_url="+repr(media_url))
        video_urls.append( [ "("+scrapertools.get_filename_from_url(media_url)[-4:]+")" , media_url ] )
    
    # Videos de archivo
    else:
        #<iframe src="https://cdnapi.shooowit.net/vdmplayer/default.iframe?injectSrc=https%3A%2F%2Fprogressive.shooowit.net%2Fremotes%2Fextremadura%2Ftv%2FESPECIALCARLOSV2019.mp4&miniature=http%3A%2F%2Fwww.canalextremadura.es%2Fsites%2Fdefault%2Ffiles%2Fstyles%2Fnuevo_dise_o_-_grande%2Fpublic%2Fimagenes-nuevo-disenio%2Ftv-a-la-carta%2Fcarlosv2019.jpg%3Fitok%3DGg4wArCB"
        player_url = scrapertools.find_single_match(data,'iframe src="([^"]+)"')
        logger.info("tvalacarta.servers.extremadura player_url="+repr(player_url))

        url_parts = urlparse.urlparse(player_url)
        logger.info("tvalacarta.servers.extremadura url_parts="+repr(url_parts))
        url_parameters = urlparse.parse_qs(url_parts.query)
        logger.info("tvalacarta.servers.extremadura url_parameters="+repr(url_parameters))

        media_url = url_parameters["injectSrc"][0]
        logger.info("media_url="+repr(media_url))
        video_urls.append( [ "("+scrapertools.get_filename_from_url(media_url)[-4:]+")" , media_url ] )

    for video_url in video_urls:
        logger.info("tvalacarta.servers.extremadura %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
