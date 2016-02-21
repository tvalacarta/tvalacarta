# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para TVG
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("[tvg.py] get_video_url(page_url='%s')" % page_url)

    if page_data=="":
        data = scrapertools.cache_page(page_url)
    else:
        data = page_data

    video_urls = []

    media_url = scrapertools.find_single_match(data,"fichero='([^']+)'")

    if media_url!="":
        video_urls.append( [ "mp4 [tvg]" , media_url ] )
    else:

        '''
        rtmp: {
        
            url: "http://www.crtvg.es/flowplayer3/flowplayer.rtmp-3.2.3.swf",
            netConnectionUrl: "rtmp://media1.crtvg.es:80/vod" //Para VOD
        },
        clip: {

            title: "A Revista FDS",
            category: "Informativos",
            subcategory: "A Revista FDS",
            eventCategory: "A Revista FDS",
            url: "mp4:00/0032/0032_20121216000000.mp4",
            provider: "rtmp",
            autoPlay: false,
            //autoBuffering: true,
            ipadUrl: "http://media1.crtvg.es:80/vod/_definst_/mp4:00/0032/0032_20121216000000.mp4/playlist.m3u8", //para ipad vod
            start: 290,
            duration: 5184,
            scaling: "scale" //scaling: orig, // fit, half, orig,scale
        }
        '''

        '''
        rtmp: {
            url: "http://www.crtvg.es/flowplayer3/flowplayer.rtmp-3.2.3.swf",
            netConnectionUrl: "rtmp://media1.crtvg.es:80/vod" //Para VOD
        },
        clip: {
            url: "mp4:00/0752/0752_20110129153400.mp4",
            provider: "rtmp",
            autoPlay: false,
            //autoBuffering: true,
            ipadUrl: "http://media1.crtvg.es:80/vod/_definst_/mp4:00/0752/0752_20110129153400.mp4/playlist.m3u8", //para ipad vod
            start: 0,
            duration: 0,
            scaling: "fit" //scaling: orig, // fit, half, orig,scale
        }
        '''
        patron  = 'rtmp\: \{.*?netConnectionUrl\: "([^"]+)"'
        matches = re.compile(patron,re.DOTALL).findall(data)
        scrapertools.printMatches(matches)
        if len(matches)==0:
            return []
        base = matches[0]
        
        patron  = 'clip\: \{.*?url\: "([^"]+)"'
        matches = re.compile(patron,re.DOTALL).findall(data)
        scrapertools.printMatches(matches)
        if len(matches)==0:
            return []
        playpath = matches[0]
        
        #rtmpdump -r rtmp://media1.crtvg.es:80/vod -y mp4:00/0032/0032_20121216000000.mp4 -s http://www.crtvg.es/flowplayer3/flowplayer.rtmp-3.2.3.swf -a vod -o ARevistaFDS.mp4
        #rtmp://media1.crtvg.es:80/vod/ playpath=mp4:00/0032/0032_20121216000000.mp4
        rtmpurl = base+"/"+playpath+" swfurl=http://www.crtvg.es/flowplayer3/flowplayer.rtmp-3.2.3.swf app=vod"
        rtmpurl = rtmpurl.replace("mp4:", " playpath=mp4:")
        
        patron  = 'clip\: \{.*?ipadUrl\: "([^"]+)"'
        matches = re.compile(patron,re.DOTALL).findall(data)
        scrapertools.printMatches(matches)
        if len(matches)==0:
            return []
        ipad = matches[0]
        
        video_urls.append( [ "RTMP [tvg]" , rtmpurl ] )
        video_urls.append( [ "iPad [tvg]" , ipad ] )

    for video_url in video_urls:
        logger.info("[tvg.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos  = '(http://www.crtvg.es/tvg/a-carta/([a-z0-9\-]+)'
    logger.info("[tvg.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[tvg]"
        url = match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'tvg' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
            
    return devuelve

