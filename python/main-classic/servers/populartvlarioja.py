# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para populartvlarioja
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

from core import logger
from core import scrapertools

from lib import youtube_dl
import vimeo

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.server.populartvlarioja get_video_url page_url"+page_url)

    video_urls = []

    data = scrapertools.cache_page(page_url)
    #https://player.vimeo.com/video/243823038?title=0&amp;byline=0&amp;portrait=0&amp;autoplay=1
    media_url = scrapertools.find_single_match(data,'iframe src="([^"]+)"')
    media_url = media_url.replace("&amp;","&")

    video_urls = vimeo.get_video_url(media_url)
    #for video_url in alternate_video_urls:
    #    video_urls.append(["[vimeo]", video_url[1]+"|User-Agent=Mozilla/5.0"])

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
