# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para sieterm
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("tvalacarta.servers.sieterm get_video_url(page_url='%s')" % page_url)
    
    data = scrapertools.cache_page(page_url)
    video_urls = []

    if "ServletLink" in page_url:
        #http://ficheros.7rm.es:3025/Video/14/1/14149_BAJA.mp4
        '''
        so.addParam('flashvars','
        &duration=3346
        &image=http://mediateca.regmurcia.com/MediatecaCRM/ServletLink?METHOD=MEDIATECA%26accion=imagen%26id=14149
        &file=media/53/Video/14/1/14149_BAJA.mp4
        &streamer=rtmp://diferido.redctnet.com/vod/mp4
        &type=rtmp
        &autostart=true
        &title=Jo Que noche!
        &description=Decai. Tete Novoa. Presuntos Implicados.');
        '''
        mediaurl = "http://ficheros.7rm.es:3025/"+scrapertools.find_single_match(data,"\&file=media/\d+/(Video[^\&]+)\&")
        video_urls.append( [ "mp4 [sieterm]" , mediaurl ] )

    else:
        mcid = scrapertools.find_single_match(data,'<div class="videoScript" data-qbrick-mcid="([^"]+)"')
        logger.info("tvalacarta.servers.sieterm mcid="+mcid)
        videoid = scrapertools.find_single_match(data,'var video\s+\=\s+"([^"]+)"')
        logger.info("tvalacarta.servers.sieterm videoid="+videoid)

        '''
        #http://vms.api.qbrick.com/rest/v3/getsingleplayer/74280B8668169fc0?statusCode=xml
        url = "http://vms.api.qbrick.com/rest/v3/getsingleplayer/"+mcid+"?statusCode=xml"

        data = scrapertools.cachePage(url)

        mediaurl = scrapertools.find_single_match(data,'<format type="download"><substream mimetype="video/mp4[^>]+>([^<]+)</substream>')
        logger.info("tvalacarta.servers.sieterm mediaurl="+mediaurl)
        '''

        #http://professional.player.qbrick.com/Html5/Web/PlayerHandler.ashx?action=getdata&embedId=qbrick_professional_qbrick1&types=mp4%2Cogg%2Cwebm&mcid=EBFEAE4968169fc0&width=720&height=405&as=0&widgetid=qbrick_professional_qbrick1&mid=EBFEAE49
        url = "http://professional.player.qbrick.com/Html5/Web/PlayerHandler.ashx?action=getdata&embedId=qbrick_professional_qbrick1&types=mp4%2Cogg%2Cwebm&mcid="+mcid+"&width=720&height=405&as=0&widgetid=qbrick_professional_qbrick1&mid="+videoid
        logger.info("tvalacarta.servers.sieterm url="+url)
        data = scrapertools.cachePage(url)
        mediaurls = scrapertools.find_single_match(data,'"substreams"\:\[([^\]]+)\]')
        logger.info("tvalacarta.servers.sieterm mediaurls="+mediaurls)

        for scrapedurl in mediaurls.split(","):
            mediaurl = scrapedurl.replace(" ","%20")
            mediaurl = mediaurl[1:-1]
            logger.info("tvalacarta.servers.sieterm mediaurl="+mediaurl)

            if mediaurl.endswith("m3u8"):
                title = "HLS"
            else:
                title = ".mp4"

            if "ipad" in mediaurl.lower():
                title = title + " (ipad)"

            if "iphone" in mediaurl.lower():
                title = title + " (iphone)"

            if "360p" in mediaurl.lower():
                title = title + " (360p)"

            if "720p" in mediaurl.lower():
                title = title + " (720p)"

            video_urls.append( [ title , mediaurl ] )

    video_urls.reverse()

    for video_url in video_urls:
        logger.info("tvalacarta.servers.sieterm %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []
            
    return devuelve

