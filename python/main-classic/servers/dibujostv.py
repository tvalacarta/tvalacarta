# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para dibujos.tv
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os
import random

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("tvalacarta.servers.dibujostv get_video_url(page_url='%s')" % page_url)
    video_urls = []

    # http://series.dibujos.tv/narigota-la-gran-aventura-del-agua/01-el-nacimiento-de-narigota-2061.html
    USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0"

    # Lee la página del vídeo
    #page_url = "http://series.dibujos.tv/narigota-la-gran-aventura-del-agua/01-el-nacimiento-de-narigota-2061.html"
    headers=[]
    headers.append(["User-Agent",USER_AGENT])
    data = scrapertools.cache_page(page_url, headers=headers)

    if not "act_cuen_prem_grande" in data:
        
        # Lee el embed
        #var idv = "2061";var width = "590";var height = "333";var rnd = (new String(Math.random())).substring(2,8) + (((new Date()).getTime()) & 262143);document.write('<scri' + 'pt language="JavaScript1.1" type="text/javascript" src="http://www.dibujos.tv/embed/?rnd='+rnd +'&idv='+idv+'&width='+width+'&height='+height+'&userid=">
        #http://www.dibujos.tv/embed/?rnd=20210045341&idv=2061&width=590&height=333&userid=
        idv = scrapertools.get_match(data,'var idv\s*=\s*"(\d+)"')
        width = scrapertools.get_match(data,'var width\s*=\s*"(\d+)"')
        height = scrapertools.get_match(data,'var height\s*=\s*"(\d+)"')
        rnd = str(random.randint(10000000000,99999999999))
        url = "http://www.dibujos.tv/embed/?rnd="+rnd+"&idv="+idv+"&width="+width+"&height="+height+"&userid="
        headers=[]
        headers.append(["User-Agent",USER_AGENT])
        headers.append(["Referer",page_url])
        bloque = scrapertools.cache_page(url, headers=headers)
        logger.info("bloque="+bloque)

        # Lee el descriptor
        url = "http://www.dibujos.tv/xmlv2/embed.php?id="+idv+"|capt1_"+width+"_"+height+".jpg|"+width+"|"+height+"|1|||0|"
        headers=[]
        headers.append(["User-Agent",USER_AGENT])
        data = scrapertools.cache_page(url, headers=headers)

        # Compone la URL
        url = scrapertools.get_match(data,"<url_video><\!\[CDATA\[([^\]]+)\]\]></url_video>")
        url = url + "|" + urllib.urlencode({"User-Agent":USER_AGENT,"Cookie":"PHPSESSID=b0d431c5006be571271f79cb93b6002a; p=a9k37djoio823jhjhf7898943o8o9edk9388j238983jj4rt89uj489"})
        logger.info("url="+url)

        video_urls.append( [ "[dibujostv]" , url , 0 , "download_and_play" ] )

    for video_url in video_urls:
        logger.info("tvalacarta.servers.dibujostv %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos  = '(http://series.dibujos.tv/.*?.html)'
    logger.info("tvalacarta.servers.dibujostv find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[dibujostv]"
        url = match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'dibujostv' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
            
    return devuelve

