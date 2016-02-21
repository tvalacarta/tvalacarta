# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para tu.tv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

# Returns an array of possible video url's from the page_url
def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[tutv.py] get_video_url(page_url='%s')" % page_url)

    # Busca el ID en la URL
    id = extract_id(page_url)
    
    # Si no lo tiene, lo extrae de la página
    if id=="":
        # La descarga
        data = scrapertools.cache_page(page_url)
        patron = '<link rel="video_src" href="([^"]+)"/>'
        matches = re.compile(patron,re.DOTALL).findall(data)
        if len(matches)>0:
            id = extract_id(matches[0])
        else:
            id = ""

    # Descarga el descriptor
    url = "http://tu.tv/visualizacionExterna2.php?web=undefined&codVideo="+id
    data = scrapertools.cache_page(url)

    # Obtiene el enlace al vídeo
    patronvideos  = 'urlVideo0=([^\&]+)\&'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    #scrapertools.printMatches(matches)
    url = urllib.unquote_plus( matches[0] )
    video_urls = [ ["[tu.tv]",url] ]

    for video_url in video_urls:
        logger.info("[tutv.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

def extract_id(text):
    patron = "xtp\=([a-zA-Z0-9]+)"
    matches = re.compile(patron,re.DOTALL).findall(text)
    if len(matches)>0:
        devuelve = matches[0]
    else:
        devuelve = ""
    
    return devuelve

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos  = '<param name="movie" value="(http://tu.tv[^"]+)"'
    logger.info("[tutv.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[tu.tv]"
        url = match
    
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'tutv' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    patronvideos  = '<param name="movie" value="(http://www.tu.tv[^"]+)"'
    logger.info("[tutv.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[tut.v]"
        url = match
    
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'tutv' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    patronvideos  = '<embed src="(http://tu.tv/[^"]+)"'
    logger.info("[tutv.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[tut.v]"
        url = match
    
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'tutv' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve
