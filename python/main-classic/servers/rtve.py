# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para rtve
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[rtve.py] get_video_url(page_url='%s')" % page_url)

    # Extrae el código
    logger.info("url="+page_url)
    codigo = scrapertools.find_single_match(page_url,'http://.*?/([0-9]+)')
    url=""
    itemlist = []
    logger.info("assetid="+codigo)

    # Código sacado de PyDownTV, gracias @aabilio :)
    # https://github.com/aabilio/PyDownTV2/blob/master/spaintvs/tve.py
    # -- Método 24 Mayo 2013
    videoID = codigo
    logger.info("Probando método de 24 de uno de Mayo de 2013")
    tipo = "videos"
    url = "http://www.rtve.es/ztnr/movil/thumbnail/default/%s/%s.png" % (tipo, videoID)

    logger.info("Probando url:"+url)
    print("Manager default")	
    from base64 import b64decode as decode
    tmp_ = decode(scrapertools.cachePage(url))
    if tmp_== "" :
        url = "http://www.rtve.es/ztnr/movil/thumbnail/anubis/%s/%s.png" % (tipo, videoID)
        tmp_ = decode(scrapertools.cachePage(url)) 
        print("Manager anubis")	
    tmp = re.findall(".*tEXt(.*)#[\x00]*([0-9]*).*", tmp_)[0]
    tmp = [n for n in tmp]
    cyphertext = tmp[0]
    key = tmp[1]
    tmp = tmp = [0 for n in range(500)]

    # Créditos para: http://sgcg.es/articulos/2012/09/11/nuevos-cambios-en-el-mecanismo-para-descargar-contenido-multimedia-de-rtve-es-2/
    intermediate_cyphertext = ""
    increment = 1
    text_index = 0
    while text_index < len(cyphertext):
        text_index = text_index + increment
        try: intermediate_cyphertext = intermediate_cyphertext + cyphertext[text_index-1]
        except: pass
        increment = increment + 1
        if increment == 5: increment = 1

    plaintext = ""
    key_index = 0
    increment = 4
    while key_index < len(key):
        key_index = key_index + 1
        text_index = int(key[key_index-1]) * 10
        key_index = key_index + increment
        try: text_index = text_index + int(key[key_index-1])
        except: pass
        text_index = text_index + 1
        increment = increment + 1
        if increment == 5: increment = 1
        try: plaintext = plaintext + intermediate_cyphertext[text_index-1]
        except: pass

    urlVideo = plaintext
    if urlVideo != "":
	url_video = urlVideo.replace("www.rtve.es", "media5.rtve.es")

	# -- CarlosJDelgado (mail@carlosjdelgado.com) -- Se obtiene la url con token tras un cambio en rtve
	url_auth = "http://flash.akamaihd.multimedia.cdn.rtve.es/auth" + urlVideo[url_video.find("/resources"):] + "?v=2.6.8&fp=WIN%2016,0,0,305&r=TDBDO&g=UZEYDOLYKFLY"
	logger.info("url_auth="+url_auth)

	urlVideo = url_video[:urlVideo.find("/resources")] + urllib2.urlopen(url_auth).read()

    else:
        logger.info("No se pudo encontrar el enlace de descarga")
    url=urlVideo
    
    logger.info("url="+url)


    # -- Método 24 Mayo 2013 FIN
    

    '''
    if url=="":
        url = "http://www.rtve.es/ztnr/consumer/xl/video/alta/" + codigo + "_es_292525252525111"
        logger.info("url="+url)

        location = scrapertools.get_header_from_response(url,header_to_get="location")

        if location != "":
            url = location.replace("www.rtve.es", "media5.rtve.es")

    if url=="":
        data = scrapertools.cache_page("http://web.pydowntv.com/api?url="+page_url)
        url = scrapertools.get_match(data,'"url_video"\: \["([^"]+)"\]')

    if url=="":
        try:
            # Compone la URL
            #http://www.rtve.es/swf/data/es/videos/alacarta/5/2/5/1/741525.xml
            url = 'http://www.rtve.es/swf/data/es/videos/alacarta/'+codigo[-1:]+'/'+codigo[-2:-1]+'/'+codigo[-3:-2]+'/'+codigo[-4:-3]+'/'+codigo+'.xml'
            logger.info("[rtve.py] url="+url)
    
            # Descarga el XML y busca el vídeo
            #<file>rtmp://stream.rtve.es/stream/resources/alacarta/flv/6/9/1270911975696.flv</file>
            data = scrapertools.cachePage(url)
            #print url
            #print data
            patron = '<file>([^<]+)</file>'
            matches = re.compile(patron,re.DOTALL).findall(data)
            scrapertools.printMatches(matches)
            if len(matches)>0:
                #url = matches[0].replace('rtmp://stream.rtve.es/stream/','http://www.rtve.es/')
                url = matches[0]
            else:
                url = ""
            
            patron = '<image>([^<]+)</image>'
            matches = re.compile(patron,re.DOTALL).findall(data)
            scrapertools.printMatches(matches)
            #print len(matches)
            #url = matches[0].replace('rtmp://stream.rtve.es/stream/','http://www.rtve.es/')
            thumbnail = matches[0]
        except:
            url = ""
    
    # Hace un segundo intento
    if url=="":
        try:
            # Compone la URL
            #http://www.rtve.es/swf/data/es/videos/video/0/5/8/0/500850.xml
            url = 'http://www.rtve.es/swf/data/es/videos/video/'+codigo[-1:]+'/'+codigo[-2:-1]+'/'+codigo[-3:-2]+'/'+codigo[-4:-3]+'/'+codigo+'.xml'
            logger.info("[rtve.py] url="+url)

            # Descarga el XML y busca el vídeo
            #<file>rtmp://stream.rtve.es/stream/resources/alacarta/flv/6/9/1270911975696.flv</file>
            data = scrapertools.cachePage(url)
            patron = '<file>([^<]+)</file>'
            matches = re.compile(patron,re.DOTALL).findall(data)
            scrapertools.printMatches(matches)
            #url = matches[0].replace('rtmp://stream.rtve.es/stream/','http://www.rtve.es/')
            url = matches[0]
        except:
            url = ""
    
    if url=="":

        try:
            # Compone la URL
            #http://www.rtve.es/swf/data/es/videos/video/0/5/8/0/500850.xml
            url = 'http://www.rtve.es/swf/data/es/videos/video/'+codigo[-1:]+'/'+codigo[-2:-1]+'/'+codigo[-3:-2]+'/'+codigo[-4:-3]+'/'+codigo+'.xml'
            logger.info("[rtve.py] url="+url)

            # Descarga el XML y busca el assetDataId
            #<plugin ... assetDataId::576596"/>
            data = scrapertools.cachePage(url)
            #logger.info("[rtve.py] data="+data)
            patron = 'assetDataId\:\:([^"]+)"'
            matches = re.compile(patron,re.DOTALL).findall(data)
            scrapertools.printMatches(matches)
            #url = matches[0].replace('rtmp://stream.rtve.es/stream/','http://www.rtve.es/')
            codigo = matches[0]
            logger.info("assetDataId="+codigo)
            
            #url = http://www.rtve.es/scd/CONTENTS/ASSET_DATA_VIDEO/6/9/5/6/ASSET_DATA_VIDEO-576596.xml
            url = 'http://www.rtve.es/scd/CONTENTS/ASSET_DATA_VIDEO/'+codigo[-1:]+'/'+codigo[-2:-1]+'/'+codigo[-3:-2]+'/'+codigo[-4:-3]+'/ASSET_DATA_VIDEO-'+codigo+'.xml'
            logger.info("[rtve.py] url="+url)
            
            data = scrapertools.cachePage(url)
            #logger.info("[rtve.py] data="+data)
            patron  = '<field>[^<]+'
            patron += '<key>ASD_FILE</key>[^<]+'
            patron += '<value>([^<]+)</value>[^<]+'
            patron += '</field>'
            matches = re.compile(patron,re.DOTALL).findall(data)
            scrapertools.printMatches(matches)
            codigo = matches[0]
            logger.info("[rtve.py] url="+url)
            
            #/deliverty/demo/resources/mp4/4/3/1290960871834.mp4
            #http://media4.rtve.es/deliverty/demo/resources/mp4/4/3/1290960871834.mp4
            #http://www.rtve.es/resources/TE_NGVA/mp4/4/3/1290960871834.mp4
            url = "http://www.rtve.es/resources/TE_NGVA"+codigo[-26:]

        except:
            url = ""
    '''

    logger.info("[rtve.py] url="+url)

    '''
    if url=="":
        logger.info("[rtve.py] Extrayendo URL tipo iPad")
        headers = []
        headers.append( ["User-Agent","Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10"] )
        location = scrapertools.get_header_from_response(page_url,headers=headers,header_to_get="location")
        logger.info("[rtve.py] location="+location)
        
        data = scrapertools.cache_page(location,headers=headers)
        logger.info("[rtve.py] data="+data)
        #<a href="/usuarios/sharesend.shtml?urlContent=/resources/TE_SREP63/mp4/4/8/1334334549284.mp4" target
        url = scrapertools.get_match(data,'<a href="/usuarios/sharesend.shtml\?urlContent\=([^"]+)" target')
        logger.info("[rtve.py] url="+url)
        #http://www.rtve.es/resources/TE_NGVA/mp4/4/8/1334334549284.mp4
        url = urlparse.urljoin("http://www.rtve.es",url)
        logger.info("[rtve.py] url="+url)
    '''
    
    video_urls = []
    video_urls.append( [ "[rtve]" , url ] )

    for video_url in video_urls:
        logger.info("[rtve.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
