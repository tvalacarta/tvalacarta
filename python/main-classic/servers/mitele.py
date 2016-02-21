# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para rtve
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urllib2,re,json

from core import logger

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[mitele.py] get_video_url(page_url='%s')" % page_url)

    # Extrae codigo fuente de la web
    videoWeb = urllib2.urlopen(page_url).read()
    #logger.info(videoWeb)

    # Extraemos ciertos elementos
    dataConfigURL = re.search('data-config[ ]*=[ ]*"(.*?)"', videoWeb).group(1)
    if dataConfigURL.startswith("/"):
        dataConfigURL = "http://www.mitele.es" + dataConfigURL
    logger.info("[mitele.py] data-config = " + dataConfigURL)

    # Obenemos el JSON del data-config
    videoJSON = json.load(urllib2.urlopen(dataConfigURL))
    #logger.info(json.dumps(videoJSON, indent = 2))

    if videoJSON["isLive"]:
        logger.info("[mitele.py] Live Stream")

        ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36"
        headers = { 'User-Agent' : ua }

        # Obtenemos la url para el token y cambiamos "dir" por "directo"
        tokenURL = videoJSON["services"]["token"].replace("dir", "directo")
        logger.info("[mitele.py] tokenURL = " + tokenURL)

        # Obtenemos el token
        tokenResult = urllib2.urlopen(urllib2.Request(tokenURL, headers = headers)).read()
        #logger.info(tokenResult)

        videoURL = re.search('videoTokenizer\({"liveUrl":"(.*?)"}\);', tokenResult).group(1).replace("\/", "/")
        logger.info("[mitele.py] Tokenized = " + videoURL)

        # Hacemos una petición a la URL tokenizada para obtener las cookies
        videoResponse = urllib2.urlopen(urllib2.Request(videoURL, headers = headers))
        logger.info("[mitele.py] Received Set-Cookie = " + videoResponse.info().getheader("Set-Cookie"))

        cookieElements = re.search('.*hdntl=(.+?);.*_alid_=(.+?);.*', videoResponse.info().getheader("Set-Cookie"))
        hdntl = cookieElements.group(1)
        alid = cookieElements.group(2)

        setCookie = "_alid_={alid}; hdntl={hdntl}".format(alid = alid, hdntl = hdntl)
        logger.info("[mitele.py] Cookie = " + setCookie)

        # Ponemos la cookie y el user-agent a la URL del vídeo
        videoURL += "|Cookie={0}&User-Agent={1}".format(setCookie, ua)
    else:
        # Y sacamos la URL del mmc
        mmcURL = videoJSON["services"]["mmc"]
        logger.info("[mitele.py] mmc = " + mmcURL)

        mmcJSON = json.load(urllib2.urlopen(mmcURL))
        #logger.info(json.dumps(mmcJSON, indent = 2))

        # Obtenemos el token
        basURL = mmcJSON["locations"][0]["bas"].partition(",")[0] + ".mp4"
        basID = basURL.split("/", 4)[4]
        logger.info("[mitele.py] basID = " + basID)

        tokenURL = "http:{gat}/?id={basID}".format(gat = mmcJSON["locations"][0]["gat"], basID = basID)
        logger.info("[mitele.py] tokenURL = " + tokenURL)

        # videoTokenizer({"tokenizedUrl":"URL"});
        tokenResult = urllib2.urlopen(tokenURL).read()
        #logger.info(tokenResult)
        videoURL = re.search('videoTokenizer\({"tokenizedUrl":"(.*?)"}\);', tokenResult).group(1).replace("\/", "/")

    video_urls = [[ "[mitele]" , videoURL ]]

    logger.info("[mitele.py] %s - %s" % (video_urls[0][0],video_urls[0][1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
