# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para EITB
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import logger
from core import scrapertools
from core.item import Item

logger.info("[eitb.py] init")

DEBUG = False
CHANNELNAME = "eitb"

def isGeneric():
    return True

def mainlist(item):
    logger.info("[eitb.py] mainlist")
    itemlist=[]

    url = 'http://www.eitb.tv/es/'

    # Descarga la página
    data = scrapertools.cachePage(url)
    patron = "<li[^>]*><a href=\"\" onclick\=\"setPlaylistId\('(\d+)','([^']+)','([^']+)'\)\;"
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for id,titulo,titulo2 in matches:
        scrapedtitle = titulo
        if titulo!=titulo2:
            scrapedtitle = scrapedtitle + " - " + titulo2
        scrapedurl = "http://www.eitb.tv/es/get/playlist/"+id
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , folder=True) )

    return itemlist

def episodios(item):
    logger.info("[eitb.py] episodios")
    itemlist=[]

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    logger.info(data)
    episodios_json = load_json(data)
    if episodios_json == None : episodios_json = []

    itemlist = []
    for video in episodios_json['videos']:
        scrapedthumbnail = video['thumbnailURL']
        if scrapedthumbnail is None:
            scrapedthumbnail = ""
        logger.info("scrapedthumbnail="+scrapedthumbnail)
        scrapedtitle = video['name']#.encode("utf-8",errors="ignore")
        #scrapedtitle = unicode( scrapedtitle , "iso-8859-1" , errors="ignore").encode("utf-8")
        
        scrapedplot = video['shortDescription']#.encode("utf8","ignore")
        try:
            scrapedtitle = video['customFields']['name_c']#.encode("utf-8","ignore")
            scrapedplot = video['customFields']['shortdescription_c']#.encode("utf-8","ignore")
        except:
            pass
        scrapedurl = "http://www.eitb.tv/es/#/video/"+str(video['id'])
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , server="eitb", url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , folder=False) )

    return itemlist

def load_json(data):
    # callback to transform json string values to utf8
    def to_utf8(dct):
        rdct = {}
        for k, v in dct.items() :
            if isinstance(v, (str, unicode)) :
                rdct[k] = v.encode('utf8', 'ignore')
            else :
                rdct[k] = v
        return rdct
    try :        
        from lib import simplejson
        json_data = simplejson.loads(data, object_hook=to_utf8)
        return json_data
    except:
        try:
            import json
            json_data = json.loads(data, object_hook=to_utf8)
            return json_data
        except:
            import sys
            for line in sys.exc_info():
                logger.error("%s" % line)

def test():

    # Al entrar sale una lista de programas
    programas_items = mainlist(Item())
    if len(programas_items)==0:
        print "Al entrar a mainlist no sale nada"
        return False

    episodios_items = episodios(programas_items[0])
    if len(episodios_items)==0:
        print "El programa "+programas_items[0].title+" no tiene episodios"
        return False

    return True