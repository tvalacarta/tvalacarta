# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para TV3
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("[tv3.py] get_video_url(page_url='%s')" % page_url)

    video_urls = []
    try:
        # --------------------------------------------------------
        # Saca el codigo de la URL y descarga
        # --------------------------------------------------------
        patron = "/videos/(\d+)/"
        matches = re.compile(patron,re.DOTALL).findall(page_url)
        scrapertools.printMatches(matches)
        codigo = matches[0]
    
        # Prueba con el modo 1
        url = geturl4(codigo)
        if url=="" or url == None:
            url = geturl3(codigo)
        if url=="" or url == None:
            url = geturl1(codigo)
        if url=="" or url == None:
            url = geturl2(codigo)
        
        if url=="" or url == None:
            return []
        
        if url.startswith("http"):
            video_urls.append( [ "HTTP [tv3]" , url ] )
            video_urls.append( [ "RTMP [tv3]" , get_url_rtmp(codigo) ] )
        else:
            #url = "rtmp://mp4-500-str.tv3.cat/ondemand/mp4:g/tvcatalunya/3/1/1269579524113.mp4"
            patron = "rtmp\:\/\/([^\/]+)\/ondemand\/mp4\:(g\/.*?mp4)"
            matches = re.compile(patron,re.DOTALL).findall(url)
            media = matches[0][1]
            
            videourl = "http://mp4-medium-dwn.media.tv3.cat/" + media
            video_urls.append( [ "HTTP [tv3]" , videourl ] )
            video_urls.append( [ "RTMP [tv3]" , get_url_rtmp(codigo) ] )
    except:  
        import traceback
        logger.info(traceback.format_exc())
        
                
    for video_url in video_urls:
        logger.info("[tv3.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

def geturl1(codigo):
    #http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID=1594629&QUALITY=H&FORMAT=FLVGES&RP=www.tv3.cat&rnd=796474
    dataurl = "http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID="+codigo+"&QUALITY=H&FORMAT=FLV&rnd=481353"
    logger.info("[tv3.py] geturl1 dataurl="+dataurl)
        
    data = scrapertools.cachePage(dataurl)
    
    patron = "(rtmp://[^\?]+)\?"
    matches = re.compile(patron,re.DOTALL).findall(data)
    url = ""
    if len(matches)>0:
        url = matches[0]
        url = url.replace('rtmp://flv-500-str.tv3.cat/ondemand/g/','http://flv-500.tv3.cat/g/')
    return url

def geturl2(codigo):
    #http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID=1594629&QUALITY=H&FORMAT=FLVGES&RP=www.tv3.cat&rnd=796474
    dataurl = "http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID="+codigo+"&QUALITY=H&FORMAT=FLVGES&RP=www.tv3.cat&rnd=796474"
    logger.info("[tv3.py] geturl2 dataurl="+dataurl)
        
    data = scrapertools.cachePage(dataurl)
    
    patron = "(rtmp://[^\?]+)\?"
    matches = re.compile(patron,re.DOTALL).findall(data)
    url = ""
    if len(matches)>0:
        url = matches[0]
        url = url.replace('rtmp://flv-es-500-str.tv3.cat/ondemand/g/','http://flv-500-es.tv3.cat/g/')
    return url

def geturl3(codigo):
    dataurl = "http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID="+codigo+"&QUALITY=H&FORMAT=MP4"
    logger.info("[tv3.py] geturl3 dataurl="+dataurl)
        
    data = scrapertools.cachePage(dataurl)
    
    patron = "(rtmp://[^\?]+)\?"
    matches = re.compile(patron,re.DOTALL).findall(data)
    url = ""
    if len(matches)>0:
        url = matches[0]
        #url = url.replace('rtmp://flv-es-500-str.tv3.cat/ondemand/g/','http://flv-500-es.tv3.cat/g/')
    return url

def geturl4(codigo):
    dataurl = "http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID="+codigo+"&QUALITY=H&FORMAT=MP4GES&RP=www.tv3.cat"
    logger.info("[tv3.py] geturl4 dataurl="+dataurl)
        
    data = scrapertools.cachePage(dataurl)
    
    patron = "(rtmp://[^\?]+)\?"
    matches = re.compile(patron,re.DOTALL).findall(data)
    url = ""
    if len(matches)>0:
        url = matches[0]
        #url = url.replace('rtmp://flv-es-500-str.tv3.cat/ondemand/g/','http://flv-500-es.tv3.cat/g/')
    return url

def get_url_rtmp(code):
    # Descarga el descriptor
    from core import scrapertools
    page_url = "http://www.tv3.cat/pvideo/FLV_bbd_dadesItem.jsp?idint="+code
    data = scrapertools.cachePage(page_url)

    logger.info("-------------------------------------------------------------------")
    logger.info(page_url)
    logger.info("-------------------------------------------------------------------")
    logger.info(data.strip())

    # Extrae el título
    patron = "<title>([^<]+)</title>"
    matches = re.findall(patron,data,flags=re.DOTALL)
    titulo = matches[0]
    logger.info("Titulo="+titulo)
    
    # Extrae el formato
    patron = '<video><format>([^<]+)</format><qualitat[^>]+>([^<]+)</qualitat>'
    matches = re.findall(patron,data,flags=re.DOTALL)
    formato = matches[0][0]
    calidad = matches[0][1]
    logger.info("Calidad="+calidad)
    logger.info("Formato="+formato)

    # Descarga el descriptor con el RTMP
    #http://www.tv3.cat/pvideo/FLV_bbd_media.jsp?PROFILE=EVP&ID=4217910&QUALITY=H&FORMAT=MP4
    #page_url = "http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID="+code+"&QUALITY="+calidad+"&FORMAT="+formato+"&rnd=8551"
    page_url = "http://www.tv3.cat/pvideo/FLV_bbd_media.jsp?PROFILE=EVP&ID="+code+"&QUALITY="+calidad+"&FORMAT="+formato+""
    data = scrapertools.cachePage(page_url)
    logger.info("-------------------------------------------------------------------")
    logger.info(page_url)
    logger.info("-------------------------------------------------------------------")
    logger.info(data.strip())

    # Extrae la url en rtmp
    patron = '<media[^>]+>([^<]+)</media>'
    matches = re.findall(patron,data,flags=re.DOTALL)
    rtmpurl = matches[len(matches)-1]
    logger.info(rtmpurl)
    
    # Averigua la extension
    patron = '.*?\.([a-z0-9]+)\?'
    matches = re.findall(patron,rtmpurl,flags=re.DOTALL)
    if len(matches)>0:
        extension = matches[0].lower()
    else:
        extension = rtmpurl[-3:]

    logger.info("Extension="+extension)
    if extension=="mp4":
        extension="flv"
    logger.info("Extension rectificada="+extension)

    #rtmpurl = "rtmp://mp4-es-500-strfs.fplive.net/mp4-es-500-str/mp4:g/tvcatalunya/6/9/1342385038696.mp4"
    # ./rtmpdump-2.4
    #     --tcUrl "rtmp://mp4-es-500-strfs.fplive.net:1935/mp4-es-500-str?ovpfv=1.1&ua=Mozilla/5.0%20%28Windows%3B%20U%3B%20Wind.ows%20NT%205.1%3B%20es-ES%3B%20rv%3A1.9.2.13%29%20Gecko/20101203%20Firefox/3.6.13"
    #     --app "mp4-es-500-str?ovpfv=1.1&ua=Mozilla/5.0%20%28Windows%3B%20U%3B%20Windows%20NT%205.1%3B%20es-ES%3B%20.rv%3A1.9.2.13%29%20Gecko/20101203%20Firefox/3.6.13"
    #     --playpath "mp4:g/tvcatalunya/6/9/1342385038696.mp4?ua=Mozilla/5.0%20%28Windows%3B%20U%3B%20Windows%20NT%205.1%3B%20es-.ES%3B%20rv%3A1.9.2.13%29%20Gecko/20101203%20Firefox/3.6.13"
    #     -o out.mp4 --host "mp4-es-500-strfs.fplive.net" --port "1935"
    patron = "rtmp\://(.*?)/(.*?)/(.*?)$"
    matches = re.findall(patron,rtmpurl,flags=re.DOTALL)
    
    host = matches[0][0]
    tcUrl = matches[0][1]
    playpath = matches[0][2]

    port = "1935"
    app = tcUrl + "?ovpfv=1.1&ua=Mozilla/5.0%20%28Windows%3B%20U%3B%20Windows%20NT%205.1%3B%20es-ES%3B%20.rv%3A1.9.2.13%29%20Gecko/20101203%20Firefox/3.6.13"
    tcUrl = "rtmp://"+host+":"+port+"/" + tcUrl + "?ovpfv=1.1&ua=Mozilla/5.0%20%28Windows%3B%20U%3B%20Wind.ows%20NT%205.1%3B%20es-ES%3B%20rv%3A1.9.2.13%29%20Gecko/20101203%20Firefox/3.6.13"
    playpath = playpath + "?ua=Mozilla/5.0%20%28Windows%3B%20U%3B%20Windows%20NT%205.1%3B%20es-.ES%3B%20rv%3A1.9.2.13%29%20Gecko/20101203%20Firefox/3.6.13"
    
    logger.info("host="+host)
    logger.info("port="+port)
    logger.info("tcUrl="+tcUrl)
    logger.info("app="+app)
    logger.info("playpath="+playpath)
    
    return "rtmp://"+host+":"+port+" tcUrl="+tcUrl+" app="+app+" playpath="+playpath

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos  = '(http://www.crtv3.es/tv3/a-carta/([a-z0-9\-]+)'
    logger.info("[tv3.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[tv3]"
        url = match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'tv3' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
            
    return devuelve

