# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para adn40
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

from core import logger
from core import scrapertools

from lib import youtube_dl

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.adn40 get_video_url(page_url='%s')" % page_url)

    ydl = youtube_dl.YoutubeDL({'outtmpl': u'%(id)s%(ext)s'})
    result = ydl.extract_info(page_url, download=False)
    logger.info("tvalacarta.server.rtve get_video_url result="+repr(result))

    video_urls = []

    if "ext" in result and "url" in result:
        video_urls.append(["[adn40]", scrapertools.safe_unicode(result['url']).encode('utf-8')])
    else:

        if "entries" in result:
            for entry in result["entries"]:
                logger.info("entry="+repr(entry))
                video_urls.append([scrapertools.safe_unicode(entry["ext"]).encode('utf-8')+" [adn40]", scrapertools.safe_unicode(entry['url']).encode('utf-8')])

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
