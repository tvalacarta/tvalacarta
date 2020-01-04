# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para rtvcm
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

from core import logger
from core import scrapertools

from lib import youtube_dl
import descargavideos

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.server.rtvcm get_video_url page_url"+page_url)

    data = scrapertools.cache_page(page_url)

    partner_id = scrapertools.find_single_match(data,'<meta property="og:image" content="https://www.kaltura.com/p/(\d+)/sp/\d+/thumbnail')
    logger.info("tvalacarta.server.rtvcm get_video_url partner_id="+partner_id)
    video_id = scrapertools.find_single_match(data,'<meta property="og:image" content="https://www.kaltura.com/p/\d+/sp/\d+/thumbnail/entry_id/([^/]+)')
    logger.info("tvalacarta.server.rtvcm get_video_url video_id="+video_id)

    media_url = "kaltura:"+partner_id+":"+video_id
    logger.info("tvalacarta.server.rtvcm get_video_url media_url="+media_url)

    ydl = youtube_dl.YoutubeDL({'outtmpl': u'%(id)s%(ext)s'})
    result = ydl.extract_info(media_url, download=False)
    logger.info("tvalacarta.server.rtvcm get_video_url result="+repr(result))

    video_urls = []

    if "ext" in result and "url" in result:
        video_urls.append(["[rtvcm]", scrapertools.safe_unicode(result['url']).encode('utf-8')+"|User-Agent=Mozilla/5.0"])
    else:

        if "entries" in result:
            for entry in result["entries"]:
                video_urls.append(["[rtvcm]", scrapertools.safe_unicode(entry['url']).encode('utf-8')+"|User-Agent=Mozilla/5.0"])

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
