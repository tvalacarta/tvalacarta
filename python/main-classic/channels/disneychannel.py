# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para disneychannel
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import logger
from core import config
from core import scrapertools
from core import jsontools
from core.item import Item

DEBUG = False
CHANNELNAME = "disneychannel"
MAIN_URL = "http://replay.disneychannel.es/"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.disneychannel mainlist")
    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.disneychannel programas")
    
    # Descarga la página
    item.url = MAIN_URL
    data = scrapertools.cache_page(item.url)
    #logger.info(data)

    data = scrapertools.find_single_match(data,'Grill.burger\=(.*?)\:\(function\(\)')
    #logger.info("data="+repr(data))
    data_json = jsontools.load_json(data)
    #logger.info("data_json="+repr(data_json))

    itemlist = []
    for bloque in data_json["stack"]:
        if bloque["view"]=="stream":

            for entry in bloque["data"]:

                if entry["type"]=="Show":
                    logger.info("entry="+repr(entry))

                    scrapedtitle = entry["title"]
                    scrapedurl = entry["href"]
                    scrapedthumbnail = entry["thumb"]

                    if "description" in entry:
                        scrapedplot = entry["description"]
                    else:
                        scrapedplot = ""
                    if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

                    # Añade al listado
                    itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot , show=scrapedtitle, viewmode="movie_with_plot", folder=True) )

    return itemlist

def detalle_episodio(item):

    data = scrapertools.cache_page(item.url)

    item.plot = scrapertools.find_single_match(data,'<meta name="description" content="([^"]+)">')
    item.thumbnail = scrapertools.find_single_match(data,'<meta property="og:image" content="([^"]+)">')

    try:
        item.duration = parse_duration_secs(scrapertools.find_single_match(data,'<meta property="video:duration" content="([^"]+)">'))
    except:
        item.duration = ""

    item.geolocked = "1"

    '''
    try:
        from servers import aragontv as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""
    '''

    return item

def episodios(item):
    logger.info("tvalacarta.channels.disneychannel episodios")
    itemlist = []

    try:
        data = scrapertools.cachePage(item.url)
        #logger.info("data="+repr(data))

        #data = scrapertools.find_single_match(data,'Grill.burger\=(.*?)\:\(function\(\)')
        # Limpia el json incorrecto
        #data = "{"+scrapertools.find_single_match(data,'("title"\:"Episodios completos","data"\:\[.*?)\,"config_options"')+"}"
        
        data = scrapertools.find_single_match(data,'(\{"view"\:"slider".*?\}),\{"view"')
        data_json = jsontools.load_json(data)
        #logger.info("data_json="+repr(data_json))

        for video in data_json["data"]:
            logger.info("video="+repr(video))

            title = video["title"]+" ("+video["duration"]+")"
            url = video["href"]
            thumbnail = video["thumb"]
            plot = video["description"]
            itemlist.append( Item(channel=CHANNELNAME, action="play", server="disneychannel", title=title, url=url, thumbnail=thumbnail, plot=plot, show=item.show, folder=False) )
    except:
        import traceback
        logger.info(traceback.format_exc())

    return itemlist

def play(item):

    item.server="disneychannel";
    itemlist = [item]

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    items_programas = mainlist(Item())
    if len(items_programas)==0:
        return False

    items_episodios = episodios(items_programas[0])
    if len(items_episodios)==0:
        return False

    return bien