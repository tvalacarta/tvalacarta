# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para eltrece
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.eltrece get_video_url(page_url='%s')" % page_url)

    video_urls = []

    # Descarga la página
    data = scrapertools.cache_page( page_url )
    data = scrapertools.find_single_match( data , '<div id="video(.*?)>')
    logger.info("tvalacarta.servers.eltrece data="+data)

    '''
    <div 
        id="video-0" 
        data-provider="cmd-lv-mp4" 
        data-uri="public://2014/12/19/noche-1.jpg" 
        data-streamer="07.vod.eltrecetv.com.ar" 
        data-nid="74346" 
        data-poster="http://eltrecetv.cdncmd.com/sites/default/files/styles/663x373/public/2014/12/19/noche-1.jpg" 
        class="loading video" 
        data-levels='[{"bitrate":"300","width":"240","height":"320","file":"2014\/12\/19\/nocheydia-jueves-181214-240.mp4"},{"bitrate":"500","width":"360","height":"480","file":"2014\/12\/19\/nocheydia-jueves-181214-360.mp4"},{"bitrate":"1500","width":"720","height":"960","file":"2014\/12\/19\/nocheydia-jueves-181214-720.mp4"}]' 
        data-desktop='2014/12/19/nocheydia-jueves-181214-720.mp4' 
        data-mobile='2014/12/19/nocheydia-jueves-181214-240.mp4'    
        data-tablet='2014/12/19/nocheydia-jueves-181214-360.mp4' 
        data-duration='3113' 
        data-streamsense='{"ci":"74346","date":"2014-12-17","ep":"Cap&iacute;tulo 18 (18-12-14)","category":"","subcategory":"","cu":"2014\/12\/19\/nocheydia-jueves-181214-720.mp4","cl":3113000,"pr":"Noche & D\u00eda"}'>
    '''
    host = scrapertools.find_single_match( data , 'data-streamer="([^"]+)"' )
    url_mobile = scrapertools.find_single_match( data , "data-mobile='([^']+)'" )
    url_tablet = scrapertools.find_single_match( data , "data-tablet='([^']+)'" )
    url_desktop = scrapertools.find_single_match( data , "data-desktop='([^']+)'" )

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
    tcUrl = "rtmp://"+host+"/vod/13tv/"
    app = "vod/13tv/"
    swfurl = "http://eltrece.cdncmd.com/sites/all/libraries/jwplayer5/player-licensed.swf"
    pageurl = page_url

    url="rtmp://" + host + " tcUrl=" + tcUrl + " app=" + app + " swfUrl=" + swfurl + " pageUrl="+pageurl + " playpath=mp4:13tv/" + url_mobile
    video_urls.append( [ "Mobile [eltrece]" , url ] )

    url="rtmp://" + host + " tcUrl=" + tcUrl + " app=" + app + " swfUrl=" + swfurl + " pageUrl="+pageurl + " playpath=mp4:13tv/" + url_tablet
    video_urls.append( [ "Tablet [eltrece]" , url ] )

    url="rtmp://" + host + " tcUrl=" + tcUrl + " app=" + app + " swfUrl=" + swfurl + " pageUrl="+pageurl + " playpath=mp4:13tv/" + url_desktop
    video_urls.append( [ "Desktop [eltrece]" , url ] )

    for video_url in video_urls:
        logger.info("tvalacarta.servers.eltrece %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve

