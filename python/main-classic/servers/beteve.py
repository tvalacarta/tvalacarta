# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para beteve
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

from core import logger
from core import scrapertools
from core import jsontools

from lib import youtube_dl

import urllib

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.beteve get_video_url(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)
    #<meta property="og:image" content="https://cdnsecakmi.kaltura.com/p/2346171/thumbnail/entry_id/1_vfk43038/height/weight/76kXI.jpg" />
    thumb = scrapertools.find_single_match(data,'<meta property="og:image" content="([^"]+)"')
    p = scrapertools.find_single_match(thumb,"p\/([^\/]+)\/")
    entry_id = scrapertools.find_single_match(thumb,"entry_id\/([^\/]+)\/")
    url = "kaltura:"+p+":"+entry_id
    
    ydl = youtube_dl.YoutubeDL({'outtmpl': u'%(id)s%(ext)s'})
    result = ydl.extract_info(page_url, download=False)
    logger.info("tvalacarta.server.beteve get_video_url result="+repr(result))

    video_urls = []
    try:
        if "ext" in result and "url" in result:
            video_urls.append(["(.m3u8)", scrapertools.safe_unicode(result['url']).encode('utf-8')+"|User-Agent=Mozilla/5.0"])
        else:

            if "entries" in result:
                for entry in result["entries"]:
                    video_urls.append(["(.m3u8)", scrapertools.safe_unicode(entry['url']).encode('utf-8')+"|User-Agent=Mozilla/5.0"])

    except:
        import traceback
        logger.info("tvalacarta.server.beteve get_video_url "+traceback.format_exc())

    for video_url in video_urls:
        logger.info("tvalacarta.servers.beteve %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
