# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para rtve
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

from core import logger
from core import scrapertools

from lib import youtube_dl
import descargavideos

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.server.rtve get_video_url page_url"+page_url)

    video_urls = []

    ydl = youtube_dl.YoutubeDL({'outtmpl': u'%(id)s%(ext)s'})
    result = ydl.extract_info(page_url, download=False)
    logger.info("tvalacarta.server.rtve get_video_url result="+repr(result))

    try:
        if "ext" in result and "url" in result:
            video_urls.append(["[rtve]", scrapertools.safe_unicode(result['url']).encode('utf-8')+"|User-Agent=Mozilla/5.0"])
        else:

            if "entries" in result:
                for entry in result["entries"]:
                    video_urls.append(["[rtve]", scrapertools.safe_unicode(entry['url']).encode('utf-8')+"|User-Agent=Mozilla/5.0"])
    except:
        import traceback
        logger.info("tvalacarta.server.rtve get_video_url "+traceback.format_exc())

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
