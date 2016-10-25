# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para rtve
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------


from core import logger
from core import scrapertools
from lib import youtube_dl

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[mitele.py] get_video_url(page_url='%s')" % page_url)

    video_urls = []
    
    ydl = youtube_dl.YoutubeDL({'outtmpl': u'%(id)s%(ext)s'})
    result = ydl.extract_info(page_url, download=False)
    logger.info("tvalacarta.server.mitele get_video_url result="+repr(result))

    if "ext" in result and "url" in result:
        for entries in result["formats"]:
            if entries["ext"] != "rtmp":
                video_url = scrapertools.safe_unicode(entries['url']).encode('utf-8')
                video_url = video_url.replace("http://ignore.mediaset.es", "http://miteleooyala-a.akamaihd.net")
                if entries["ext"] != "mp4":
                    title = scrapertools.safe_unicode(entries["format"]).encode('utf-8')
                elif entries["ext"] == "mp4":
                    if entries.has_key("vbr"):
                        title = "mp4-" + scrapertools.safe_unicode(str(entries["vbr"])).encode('utf-8') + " " + scrapertools.safe_unicode(entries["format"]).encode('utf-8').rsplit("-",1)[1]
                    else:
                        title = scrapertools.safe_unicode(entries["format"]).encode('utf-8')

                try:
                    calidad = int(scrapertools.safe_unicode(str(entries["vbr"])))
                except:
                    try:
                        calidad = int(title.split("-")[1].strip())
                    except:
                        calidad = 3000
                video_urls.append(["%s" % title, video_url, 0, False, calidad])
                
    video_urls.sort(key=lambda video_urls: video_urls[4], reverse=True)
    for url in video_urls:
        logger.info("[mitele.py] %s - %s" % (url[0],url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
