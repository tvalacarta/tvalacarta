# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para aragontv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("[aragontv.py] get_video_url(page_url='%s')" % page_url)

    # ANTES
    #url:'mp4%3A%2F_archivos%2Fvideos%2Fweb%2F2910%2F2910.mp4',
    #netConnectionUrl: 'rtmp%3A%2F%2Falacarta.aragontelevision.es%2Fvod'
    #rtmp://iasoftvodfs.fplive.net/iasoftvod/web/980/980.mp4

    # AHORA
    #{ url:'mp4%3A%2Fweb%2F5573%2F5573.mp4', provider: 'rtmp' }
    #netConnectionUrl: 'rtmp%3A%2F%2Faragontvvodfs.fplive.net%2Faragontvvod'
    #rtmp://aragontvvodfs.fplive.net/aragontvvod/web/980/980.mp4
    
    itemlist = []

    # Mira a ver si es una página normal    
    url = get_video_url_from_page(page_url)

    # Ahora prueba con página de videos del curso de inglés, que se calculan de forma distinta
    # debido a un error en la web de Aragón TV
    # El problema es que no aparece la URL completa, y hay que deducirla
    if url == "":
        # Extrae el titulo del video de la URL
        # http://alacarta.aragontelevision.es/nivel-basico-i-cap-65-parte-2-30092012-1014
        # nivel-basico-i-cap-65-parte-2-30092012-1014
        fragmentos = page_url.split("/")
        titulo = fragmentos[ len(fragmentos)-1 ]
        logger.info("titulo="+titulo)

        if "basico-i-" in titulo:
            page_url = "http://alacarta.aragontelevision.es/programas/vaughan/basico-i/"+titulo
        elif "basico-ii-" in titulo:
            page_url = "http://alacarta.aragontelevision.es/programas/vaughan/basico-ii/"+titulo
        elif "intermedio-i-" in titulo:
            page_url = "http://alacarta.aragontelevision.es/programas/vaughan/intermedio-i/"+titulo
        elif "intermedio-ii-" in titulo:
            page_url = "http://alacarta.aragontelevision.es/programas/vaughan/intermedio-ii/"+titulo
        elif "stuff-" in titulo:
            page_url = "http://alacarta.aragontelevision.es/programas/vaughan/stuff/"+titulo
        elif "common-mistakes-" in titulo:
            page_url = "http://alacarta.aragontelevision.es/programas/vaughan/common-mistakes/"+titulo

        # Prueba de nuevo
        url = get_video_url_from_page(page_url)

    if url == "":        
        # Si aun así no funciona, tendrá que probar con todos los programas para ver cual es el bueno
        page_url = "http://alacarta.aragontelevision.es/programas/vaughan/basico-i/"+titulo
        url = get_video_url_from_page(page_url)

        if url=="":
            page_url = "http://alacarta.aragontelevision.es/programas/vaughan/basico-ii/"+titulo
            url = get_video_url_from_page(page_url)
        if url=="":
            page_url = "http://alacarta.aragontelevision.es/programas/vaughan/intermedio-i/"+titulo
            url = get_video_url_from_page(page_url)
        if url=="":
            page_url = "http://alacarta.aragontelevision.es/programas/vaughan/intermedio-ii/"+titulo
            url = get_video_url_from_page(page_url)
        if url=="":
            page_url = "http://alacarta.aragontelevision.es/programas/vaughan/stuff/"+titulo
            url = get_video_url_from_page(page_url)
        if url=="":
            page_url = "http://alacarta.aragontelevision.es/programas/vaughan/common-mistakes/"+titulo
            url = get_video_url_from_page(page_url)

    video_urls = []
    if url != "":
        video_urls.append( [ "para Web (rtmp) [aragontv]" , url ] )

    for video_url in video_urls:
        logger.info("[aragontv.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

def get_video_url_from_page(page_url):
    # Descarga la página
    data = scrapertools.cache_page(page_url)

    try:
        final = scrapertools.get_match(data,"url\:'(mp4\%3A[^']+)'")
        principio = scrapertools.get_match(data,"netConnectionUrl\: '([^']+)'")

        if urllib.unquote(principio).startswith("rtmp://aragon") or urllib.unquote(principio).startswith("rtmp://iasoft"):
            url = principio+"/"+final[9:]
        else:
            url = principio+"/"+final
        url = urllib.unquote(url)
        logger.info("url="+url)
    except:
        url = ""
        logger.info("url NO encontrada")

    return url

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve

