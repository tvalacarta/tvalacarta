# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Conector para telefe
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.telefe get_video_url(page_url='%s')" % page_url)
    video_urls = []

    # Descarga la página del vídeo
    data = scrapertools.cache_page(page_url)

    # Esquema normal
    bloque = scrapertools.get_match(data,'sources(.*?)\]')
    patron = '"file"\s*\:\s*"([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for match in matches:
        tipo = match[:4]
        url = match
        if tipo=="rtmp":
            url=url.replace("mp4:TOK","TOK")

        video_urls.append( [ tipo+" [telefe]" , url ] )

        '''
        00:55:30 T:2955980800   ERROR: Valid RTMP options are:
        00:55:30 T:2955980800   ERROR:      socks string   Use the specified SOCKS proxy
        00:55:30 T:2955980800   ERROR:        app string   Name of target app on server
        00:55:30 T:2955980800   ERROR:      tcUrl string   URL to played stream
        00:55:30 T:2955980800   ERROR:    pageUrl string   URL of played media's web page
        00:55:30 T:2955980800   ERROR:     swfUrl string   URL to player SWF file
        00:55:30 T:2955980800   ERROR:   flashver string   Flash version string (default MAC 10,0,32,18)
        00:55:30 T:2955980800   ERROR:       conn AMF      Append arbitrary AMF data to Connect message
        00:55:30 T:2955980800   ERROR:   playpath string   Path to target media on server
        00:55:30 T:2955980800   ERROR:   playlist boolean  Set playlist before play command
        00:55:30 T:2955980800   ERROR:       live boolean  Stream is live, no seeking possible
        00:55:30 T:2955980800   ERROR:  subscribe string   Stream to subscribe to
        00:55:30 T:2955980800   ERROR:        jtv string   Justin.tv authentication token
        00:55:30 T:2955980800   ERROR:       weeb string   Weeb.tv authentication token
        00:55:30 T:2955980800   ERROR:      token string   Key for SecureToken response
        00:55:30 T:2955980800   ERROR:     swfVfy boolean  Perform SWF Verification
        00:55:30 T:2955980800   ERROR:     swfAge integer  Number of days to use cached SWF hash
        00:55:30 T:2955980800   ERROR:    swfsize integer  Size of the decompressed SWF file
        00:55:30 T:2955980800   ERROR:    swfhash string   SHA256 hash of the decompressed SWF file
        00:55:30 T:2955980800   ERROR:      start integer  Stream start position in milliseconds
        00:55:30 T:2955980800   ERROR:       stop integer  Stream stop position in milliseconds
        00:55:30 T:2955980800   ERROR:     buffer integer  Buffer time in milliseconds
        00:55:30 T:2955980800   ERROR:    timeout integer  Session timeout in seconds
        '''

    if len(video_urls)>0:
        for video_url in video_urls:
            logger.info("tvalacarta.servers.telefe %s - %s" % (video_url[0],video_url[1]))
        return video_urls

    for video_url in video_urls:
        for video_url in video_urls:
            logger.info("tvalacarta.servers.telefe %s - %s" % (video_url[0],video_url[1]))
        logger.info("tvalacarta.servers.telefe %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # divxstage http://www.divxstage.net/video/2imiqn8w0w6dx"
    patronvideos  = 'http://www.divxstage.[\w]+/video/([\w]+)'
    logger.info("tvalacarta.servers.telefe find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[telefe]"
        url = "http://www.divxstage.net/video/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'divxstage' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
            
    return devuelve
