# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para youtube
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import re
from core import scrapertools
from core import logger
from core import config
from lib import youtube_dl

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.youtube get_video_url page_url="+page_url)

    if not page_url.startswith("http"):
        page_url = "http://www.youtube.com/watch?v="+page_url
        logger.info("tvalacarta.servers.youtube get_video_url page_url="+page_url)

    # Quita la playlist
    if "&list=" in page_url:
        import re
        page_url = re.compile("\&list\=[A-Za-z0-9\-_]+",re.DOTALL).sub("",page_url)
        logger.info("tvalacarta.servers.youtube get_video_url page_url="+page_url)

    if "?list=" in page_url:
        import re
        page_url = re.compile("\?list\=[^\&]+&",re.DOTALL).sub("?",page_url)
        logger.info("tvalacarta.servers.youtube get_video_url page_url="+page_url)

    ydl = youtube_dl.YoutubeDL({'outtmpl': u'%(id)s%(ext)s'})
    result = ydl.extract_info(page_url, download=False)
    logger.info("result="+repr(result))

    video_urls = []
    if 'formats' in result:
        for entry in result['formats']:
            logger.info("entry="+repr(entry))

            extension = ""

            try:
                if entry['ext'] is not None:
                    extension = scrapertools.safe_unicode("("+entry['ext']+")").encode('utf-8')
            except:
                import traceback
                logger.info(traceback.format_exc())

            resolution = ""

            try:
                if entry['width'] is not None and entry['height'] is not None:
                    resolution = scrapertools.safe_unicode(" ("+str(entry['width'])+"x"+str(entry['height'])+")").encode('utf-8')
            except:
                import traceback
                logger.info(traceback.format_exc())

            tag = ""

            try:
                if entry['acodec']=='none':
                    tag=" (Solo video)"

                if entry['vcodec']=='none':
                    tag=" (Solo audio)"

                if config.get_setting("youtube_special_formats")=="false" and tag<>"":
                    continue

            except:
                import traceback
                logger.info(traceback.format_exc())

            video_urls.append([ extension+resolution+tag , scrapertools.safe_unicode(entry['url']).encode('utf-8')])

    video_urls.reverse()

    return video_urls

def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos  = 'youtube(?:-nocookie)?\.com/(?:(?:(?:v/|embed/))|(?:(?:watch(?:_popup)?(?:\.php)?)?(?:\?|#!?)(?:.+&)?v=))?([0-9A-Za-z_-]{11})'#'"http://www.youtube.com/v/([^"]+)"'
    logger.info("[youtube.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[YouTube]"
        url = "http://www.youtube.com/watch?v="+match
        
        if url!='':
            if url not in encontrados:
                logger.info("  url="+url)
                devuelve.append( [ titulo , url , 'youtube' ] )
                encontrados.add(url)
            else:
                logger.info("  url duplicada="+url)
    
    patronvideos  = 'www.youtube.*?v(?:=|%3D)([0-9A-Za-z_-]{11})'
    logger.info("[youtube.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[YouTube]"
        url = "http://www.youtube.com/watch?v="+match

        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'youtube' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    #http://www.youtube.com/v/AcbsMOMg2fQ
    patronvideos  = 'youtube.com/v/([0-9A-Za-z_-]{11})'
    logger.info("[youtube.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[YouTube]"
        url = "http://www.youtube.com/watch?v="+match

        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'youtube' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve
