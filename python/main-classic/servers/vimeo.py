# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para Vimeo
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os
import socket
from xml.dom.minidom import parseString

from core import scrapertools
from core import logger
from core import config

# Returns an array of possible video url's from the page_url
def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[vimeo.py] get_video_url(page_url='%s')" % page_url)

    video_urls = []

    if page_url.startswith("http://"):
        videoid = extract_video_id(page_url)
    else:
        videoid = page_url
    url = "http://www.vimeo.com/moogaloop/load/clip:%s/local/" % videoid
    
    headers = [ ['User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'],['Referer','http://vimeo/%s' % page_url] ]
    data = scrapertools.cache_page(url, headers=headers)

    #parseamos el xml en busca del codigo de signatura
    dom = parseString(data);
    xml = dom.getElementsByTagName("xml")

    for node in xml:
        try:
            request_signature = getNodeValue(node, "request_signature", "Unknown Uploader").encode( "utf-8" )
            request_signature_expires = getNodeValue(node, "request_signature_expires", "Unknown Uploader").encode( "utf-8")
        except:
            logger.info("Error : Video borrado")
            return ""

    # Extrae las dos calidades (SD y HD)
    video_url = resolve_video_link(videoid,request_signature,request_signature_expires,"sd")
    if len(video_url) > 0:
        video_urls.append( ["SD [vimeo]",video_url])

    video_url = resolve_video_link(videoid,request_signature,request_signature_expires,"hd")
    if len(video_url) > 0:
        video_urls.append( ["HD [vimeo]",video_url])


    for video_url in video_urls:
        logger.info("[videobb.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

def resolve_video_link(videoid,request_signature,request_signature_expires,quality):
    #http://player.vimeo.com/play_redirect?clip_id=19284716&sig=876501f707e219dc48ae78efc83329c3&time=1297504613&quality=hd&codecs=H264,VP8,VP6&type=moogaloop_local&embed_location=
    video_url = "http://player.vimeo.com/play_redirect?clip_id=%s&sig=%s&time=%s&quality=%s&codecs=H264,VP8,VP6&type=moogaloop_local&embed_location=" % ( videoid, request_signature, request_signature_expires , quality )
    logger.info("[vimeo.py] video_url="+video_url)
    txheaders =  {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
                  'Host':'player.vimeo.com'}
    
    #buscamos la url real en el headers
    txdata=None
    req = urllib2.Request(video_url, txdata, txheaders)
    
    try:
        opener = urllib2.build_opener(SmartRedirectHandler())
        response = opener.open(req)
    except ImportError, inst:
        status,location=inst
        logger.info(str(status) + " " + location)    
        mediaurl = location    
        
    # Timeout del socket a 60 segundos
    socket.setdefaulttimeout(10)

    h=urllib2.HTTPHandler(debuglevel=0)
    request = urllib2.Request(mediaurl)

    opener = urllib2.build_opener(h)
    urllib2.install_opener(opener)
    try:
        connexion = opener.open(request)
        video_url = connexion.geturl()
    except urllib2.HTTPError,e:
        logger.info.output("[vimeo.py]  error %d (%s) al abrir la url %s" % (e.code,e.msg,video_url))
        logger.info( e.read() )

    return video_url

class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        raise ImportError(302,headers.getheader("Location"))
        
def getNodeValue(node, tag, default = ""):
        if node.getElementsByTagName(tag).item(0):
            if node.getElementsByTagName(tag).item(0).firstChild:
                return node.getElementsByTagName(tag).item(0).firstChild.nodeValue

def extract_video_id(url):
    #http://vimeo.com/27307766
    patron = 'http://vimeo.com/([0-9]+)'
    matches = re.compile(patron,re.DOTALL).findall(url)
    
    if len(matches)>0:
        return matches[0]
    else:
        return ""

# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    #"http://player.vimeo.com/video/17555432?title=0&amp;byline=0&amp;portrait=0
    patronvideos  = 'http://player.vimeo.com/video/([0-9]+)'
    logger.info("[vimeo.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(text)

    for match in matches:
        titulo = "[vimeo]"
        url = "http://vimeo.com/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'vimeo' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            

    #"http://vimeo.com/17555432
    patronvideos  = 'http://vimeo.com/([0-9]+)'
    logger.info("[vimeo.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(text)

    for match in matches:
        titulo = "[vimeo]"
        url = "http://vimeo.com/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'vimeo' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
    return devuelve
