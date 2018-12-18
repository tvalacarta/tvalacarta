# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para populartvcantabria
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

from core import logger
from core import scrapertools

from lib import youtube_dl
import descargavideos

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.server.populartvcantabria get_video_url page_url"+page_url)

    data = scrapertools.cache_page(page_url)
    video_id = scrapertools.find_single_match(data,'data-video_id="([^"]+)"')
    logger.info("tvalacarta.server.populartvcantabria video_id="+video_id)
    youtube_url = "https://www.youtube.com/watch?v="+video_id
    logger.info("tvalacarta.server.populartvcantabria youtube_url="+youtube_url)

    ydl = youtube_dl.YoutubeDL({'outtmpl': u'%(id)s%(ext)s'})
    result = ydl.extract_info(youtube_url, download=False)
    video_urls = []
    if 'formats' in result:
        for entry in result['formats']:
            logger.info("entry="+repr(entry))
            if 'http' in entry['protocol']:
                video_urls.append([scrapertools.safe_unicode(entry['format']).encode('utf-8'), scrapertools.safe_unicode(entry['url']).encode('utf-8')])
                #logger.info('Append: {}'.format(entry['url']))

    video_urls.reverse()

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
