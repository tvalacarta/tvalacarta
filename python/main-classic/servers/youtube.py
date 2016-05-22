# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para youtube
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

from core import scrapertools
from core import logger

try:
    import youtube_dl
except:
    from lib import youtube_dl

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.youtube get_video_url page_url="+page_url)

    if not page_url.startswith("http"):
        page_url = "http://www.youtube.com/watch?v="+page_url

    ydl = youtube_dl.YoutubeDL({'outtmpl': u'%(id)s%(ext)s'})
    result = ydl.extract_info(page_url, download=False)
    video_urls = []
    if 'formats' in result:
        for entry in result['formats']:
            logger.info("entry="+repr(entry))
            video_urls.append([scrapertools.safe_unicode(entry['format']).encode('utf-8'), scrapertools.safe_unicode(entry['url']).encode('utf-8')])

    video_urls.reverse()

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
