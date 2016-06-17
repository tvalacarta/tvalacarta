# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para cntv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import re, sys
import urlparse, urllib, urllib2

from core import scrapertools
from core import logger
from core import config
from core import jsontools

def get_video_url( page_url , premium = False , user="" , password="" , video_password="" ):
    logger.info("tvalacarta.servers.cntv get_video_url(page_url='%s')" % page_url)

    if page_url.startswith("http://"):
        data = scrapertools.cache_page(page_url)
        video_id = scrapertools.find_single_match(data,'"videoCenterId","([a-z0-9]+)"')
    else:
        video_id = page_url
        page_url = ""

    logger.info("tvalacarta.servers.cntv video_id="+video_id)

    video_url_m3u8 = ""
    video_url_mp4_high = ""
    video_url_mp4_low = ""

    # Formato noticias
    if video_id!="":
        metadata_url = "http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid="+video_id+"&tz=-1&from=000spanish&url="+page_url+"&idl=32&idlr=32&modifyed=false"
        data = scrapertools.cache_page(metadata_url)
        logger.info(data)
    
        json_data = jsontools.load_json(data)

        #video_url_m3u8 = scrapertools.find_single_match(data,'"hls_url"\:"([^"]+)"')
        video_url_m3u8 = json_data['hls_url']
        video_url_mp4_high = json_data['video']['chapters'][0]['url']
        try:
            video_url_mp4_low = json_data['video']['lowChapters'][0]['url']
        except:
            video_url_mp4_low = ""

    # Formato programas
    else:
        video_id = scrapertools.find_single_match(data,'"videoCenterId","(.*?)"')
        video_url_m3u8 = "http://asp.v.cntv.cn/hls/"+matches[0]+"/main.m3u8"

    logger.info("video_url_m3u8="+video_url_m3u8)
    logger.info("video_url_mp4_high="+video_url_mp4_high)
    logger.info("video_url_mp4_low="+video_url_mp4_low)

    lista_videourls = []

    if video_url_mp4_low!="":
        lista_videourls.append([ 'LOW ('+scrapertools.get_filename_from_url(video_url_mp4_low)[-4:] + ') [cntv]' , video_url_mp4_low])

    if video_url_mp4_high!="":
        lista_videourls.append([ 'HIGH ('+scrapertools.get_filename_from_url(video_url_mp4_high)[-4:] + ') [cntv]' , video_url_mp4_high])


    if ".m3u8" in video_url_m3u8:
        data_calidades = scrapertools.cache_page(video_url_m3u8)
        patron_calidades = "BANDWIDTH=(\d+), RESOLUTION=([a-z0-9]+)\s*(.*?.m3u8)"
        matches = re.compile(patron_calidades,re.DOTALL).findall(data_calidades)

        if len(matches)>0:
            for bitrate,resolucion,calidad_url in matches:
                esta_url = urlparse.urljoin(video_url_m3u8,calidad_url)
                try:
                    kb = " "+str(int(bitrate)/1024)+"Kbps "
                except:
                    kb = ""

                lista_videourls.append([ resolucion + kb + '('+scrapertools.get_filename_from_url(esta_url)[-4:] + ') [cntv]' , esta_url])
        else:
            lista_videourls.append([ '('+scrapertools.get_filename_from_url(video_url_m3u8)[-4:] + ') [cntv]' , video_url_m3u8])

    else:
        lista_videourls.append([ '('+scrapertools.get_filename_from_url(video_url_m3u8)[-4:] + ') [cntv]' , video_url_m3u8])

    lista_videourls.reverse()

    for v in lista_videourls:
        logger.info("tvalacarta.servers.cntv %s - %s" % (v[0],v[1]))

    return lista_videourls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    logger.info("tvalacarta.servers.cntv find_videos")

    encontrados = set()
    devuelve = []

    return devuelve

def test():
    video_urls = get_video_url("http://espanol.cntv.cn/program/ArteCulinarioChino/20130806/102791.shtml")
    return len(video_urls)>0
