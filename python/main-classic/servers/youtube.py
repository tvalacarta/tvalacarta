# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#
# Conector para Youtube
#
# La técnica ha sido extraída del add-on oficial de YouTube
# hecho por Tobias Ussing y Henrik Mosgaard Jensen
# Gracias por resolverlo, y hacerlo open source :)
#------------------------------------------------------------
import urlparse,urllib2,urllib,re,httplib
from core import config
from core import logger
from core import scrapertools
from core.item import Item

import cgi
try:
    import simplejson as json
except ImportError:
    import json

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[youtube.py] get_video_url(page_url='%s')" % page_url)
    video_urls = []

    #page_url = "http://www.youtube.com/get_video_info?&video_id=zlZgGlwBgro"
    if not page_url.startswith("http"):
        page_url = "http://www.youtube.com/watch?v=%s" % page_url
        logger.info("[youtube.py] page_url->'%s'" % page_url)
        
    # Lee la página del video
    data = scrapertools.cache_page( page_url , headers=[['User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3']] , )
    video_urls = scrapeWebPageForVideoLinks(data)

    video_urls.reverse()
    
    for video_url in video_urls:
        logger.info(str(video_url))
    
    return video_urls

def removeAdditionalEndingDelimiter(data):
    pos = data.find("};")
    if pos != -1:
        logger.info("found extra delimiter, removing")
        data = data[:pos + 1]
    return data

def extractFlashVars(data):
    flashvars = {}
    #found = False
    patron = '<script>.*?ytplayer.config = (.*?);</script>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if matches:
        data = matches[0]
        data = removeAdditionalEndingDelimiter(data)
        data = json.loads(data)
        flashvars = data["args"]
    '''
    def extractFlashVars(self, data):
        flashvars = {}
        found = False

        for line in data.split("\n"):
            if line.strip().find(";ytplayer.config = ") > 0:
                found = True
                p1 = line.find(";ytplayer.config = ") + len(";ytplayer.config = ") - 1
                p2 = line.rfind(";")
                if p1 <= 0 or p2 <= 0:
                    continue
                data = line[p1 + 1:p2]
                break
        data = self.removeAdditionalEndingDelimiter(data)

        if found:
            data = json.loads(data)
            flashvars = data["args"]
        self.common.log("Step2: " + repr(data))

        self.common.log(u"flashvars: " + repr(flashvars), 2)
        return flashvars
    '''
    logger.info("flashvars: " + repr(flashvars))
    return flashvars

def scrapeWebPageForVideoLinks(data):
    logger.info("")
    links = {}

    fmt_value = {
        5: "240p h263 flv",
        18: "360p h264 mp4",
        22: "720p h264 mp4",
        26: "???",
        33: "???",
        34: "360p h264 flv",
        35: "480p h264 flv",
        37: "1080p h264 mp4",
        36: "3gpp",
        38: "720p vp8 webm",
        43: "360p h264 flv",
        44: "480p vp8 webm",
        45: "720p vp8 webm",
        46: "520p vp8 webm",
        59: "480 for rtmpe",
        78: "400 for rtmpe",
        82: "360p h264 stereo",
        83: "240p h264 stereo",
        84: "720p h264 stereo",
        85: "520p h264 stereo",
        100: "360p vp8 webm stereo",
        101: "480p vp8 webm stereo",
        102: "720p vp8 webm stereo",
        120: "hd720",
        121: "hd1080"
        }

    video_urls=[]

    flashvars = extractFlashVars(data)
    if not flashvars.has_key(u"url_encoded_fmt_stream_map"):
        return links

    if flashvars.has_key(u"ttsurl"):
        logger.info("ttsurl="+flashvars[u"ttsurl"])

    for url_desc in flashvars[u"url_encoded_fmt_stream_map"].split(u","):
        url_desc_map = cgi.parse_qs(url_desc)
        logger.info(u"url_map: " + repr(url_desc_map))
        if not (url_desc_map.has_key(u"url") or url_desc_map.has_key(u"stream")):
            continue

        try:
            key = int(url_desc_map[u"itag"][0])
            url = u""
            if url_desc_map.has_key(u"url"):
                url = urllib.unquote(url_desc_map[u"url"][0])
            elif url_desc_map.has_key(u"conn") and url_desc_map.has_key(u"stream"):
                url = urllib.unquote(url_desc_map[u"conn"][0])
                if url.rfind("/") < len(url) -1:
                    url = url + "/"
                url = url + urllib.unquote(url_desc_map[u"stream"][0])
            elif url_desc_map.has_key(u"stream") and not url_desc_map.has_key(u"conn"):
                url = urllib.unquote(url_desc_map[u"stream"][0])

            if url_desc_map.has_key(u"sig"):
                url = url + u"&signature=" + url_desc_map[u"sig"][0]

            #links[key] = url
            video_urls.append( [ "("+fmt_value[key]+") [youtube]" , url ])
        except:
            logger.info("ERROR EN "+str(url_desc))

    # La calidad más alta la primera
    video_urls.reverse()

    return video_urls

def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos  = 'youtube(?:-nocookie)?\.com/(?:(?:(?:v/|embed/))|(?:(?:watch(?:_popup)?(?:\.php)?)?(?:\?|#!?)(?:.+&)?v=))?([0-9A-Za-z_-]{11})'#'"http://www.youtube.com/v/([^"]+)"'
    logger.info("[youtube.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[YouTube]"
        url = "http://www.youtube.com/watch?v="+match
        
        if url!='':
            if url not in encontrados:
                logger.info("  url="+url)
                devuelve.append( [ titulo , url , 'youtube' ] )
                encontrados.add(url)
            else:
                logger.info("  url duplicada="+url)
    
    patronvideos  = 'www.youtube.*?v(?:=|%3D)([0-9A-Za-z_-]{11})'
    logger.info("[youtube.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[YouTube]"
        url = "http://www.youtube.com/watch?v="+match

        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'youtube' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    #http://www.youtube.com/v/AcbsMOMg2fQ
    patronvideos  = 'youtube.com/v/([0-9A-Za-z_-]{11})'
    logger.info("[youtube.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[YouTube]"
        url = "http://www.youtube.com/watch?v="+match

        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'youtube' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve

def test():
    video_urls = get_video_url("http://www.youtube.com/watch?v=Kk-435429-M")
    return len(video_urls)>0