# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para 8TV
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import re
import sys
import os
import traceback
import urllib2

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "vuittv"
__category__ = "R"
__type__ = "generic"
__title__ = "8TV"
__language__ = "ES"
__creationdate__ = "20160928"

DEBUG = config.get_setting("debug")

URL_LIVE  = "rtmp://streaming.8tv.cat:1935/8TV?videoId=3998198240001&lineUpId=&pubId=1589608506001&playerId=1982328835001&affiliateId=/8aldia-directe?videoId=3998198240001&lineUpId=&pubId=1589608506001&playerId=1982328835001&affiliateId="

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.8tv mainlist")

    itemlist = []

    itemlist.append( Item(channel=__channel__, title="8tv directe",              action="play",         url = URL_LIVE,                                            folder=False) )
    itemlist.append( Item(channel=__channel__, title="8aldia Inici (destacat)",  action="loadprogram",  url = "http://www.8tv.cat/8aldia/",                        folder=True) )
    itemlist.append( Item(channel=__channel__, title="8aldia Reflexió Cuní",     action="loadprogram",  url = "http://www.8tv.cat/8aldia/reflexio-de-josep-cuni/", folder=True) )
    itemlist.append( Item(channel=__channel__, title="8aldia Seccions",          action="loadsections",                                                            folder=True) )
    itemlist.append( Item(channel=__channel__, title="8aldia Programes sencers", action="loadprogram",  url = "http://www.8tv.cat/8aldia/programes-sencers/",      folder=True) )

    return itemlist


# Carga secciones
def loadsections(item):
    logger.info("tvalacarta.channels.8tv loadsection")

    itemlist = []

    itemlist.append( Item(channel=__channel__, title="Entrevistes",   action="loadprogram", url="http://www.8tv.cat/8aldia/category/entrevistes/",     folder=True) )
    itemlist.append( Item(channel=__channel__, title="Pilar Rahola",  action="loadprogram", url="http://www.8tv.cat/8aldia/category/pilar-rahola/",    folder=True) )
    itemlist.append( Item(channel=__channel__, title="La Tertúlia",   action="loadprogram", url="http://www.8tv.cat/8aldia/category/tertulia/",        folder=True) )
    itemlist.append( Item(channel=__channel__, title="Opinió",        action="loadprogram", url="http://www.8tv.cat/8aldia/category/opinio/",          folder=True) )
    itemlist.append( Item(channel=__channel__, title="Política",      action="loadprogram", url="http://www.8tv.cat/8aldia/category/politica/",        folder=True) )
    itemlist.append( Item(channel=__channel__, title="Internacional", action="loadprogram", url="http://www.8tv.cat/8aldia/category/internacional/",   folder=True) )
    itemlist.append( Item(channel=__channel__, title="Economia",      action="loadprogram", url="http://www.8tv.cat/8aldia/category/economia-videos/", folder=True) )
    itemlist.append( Item(channel=__channel__, title="Societat",      action="loadprogram", url="http://www.8tv.cat/8aldia/category/societat/",        folder=True) )
    itemlist.append( Item(channel=__channel__, title="Successos",     action="loadprogram", url="http://www.8tv.cat/8aldia/category/successos/",       folder=True) )
    itemlist.append( Item(channel=__channel__, title="Tribunals",     action="loadprogram", url="http://www.8tv.cat/8aldia/category/tribunals/",       folder=True) )
    itemlist.append( Item(channel=__channel__, title="Cultura",       action="loadprogram", url="http://www.8tv.cat/8aldia/category/cultura/",         folder=True) )
    itemlist.append( Item(channel=__channel__, title="Tecnologia",    action="loadprogram", url="http://www.8tv.cat/8aldia/category/tecnologia/",      folder=True) )
    itemlist.append( Item(channel=__channel__, title="Esports",       action="loadprogram", url="http://www.8tv.cat/8aldia/category/esports/",         folder=True) )

    return itemlist


# Carga programas de una sección
def loadprogram(item):
    logger.info("tvalacarta.channels.8tv loadprogram")
    return pager(item.url, item.channel, item)


# Genera listado de los videos con paginador
def pager(url, channel=__channel__, item=None):
    logger.info("tvalacarta.channels.8tv pager")

    try:
        itemlist = []
        data = scrapertools.downloadpage(url)
        data = data.replace("\\\"","")
        #logger.error("DATA: " + str(data))

        # --------------------------------------------------------
        # Extrae los videos (tag article)
        # --------------------------------------------------------
        patron = '<article class="entry-box entry-video (.*?)</article>'
        matches = re.compile(patron,re.DOTALL).findall(data)

        if len(matches) > 0:
            for chapter in matches:
                try:
                    #
                    # Ex: <h2 class="entry-title"><a href="http://www.8tv.cat/8aldia/videos/el-proxim-11-de-setembre-marcat-pel-referendum/" title="El pròxim 11 de Setembre, marcat pel referèndum">
                    #
                    patron = ' src="([^"]+)"'
                    matches = re.compile(patron,re.DOTALL).findall(chapter)
                    scrapedthumbnail = matches[0]

                    patron = '<h2 class="entry-title"><a href="([^"]+)" title="([^"]+)">'
                    matches = re.compile(patron,re.DOTALL).findall(chapter)
                    urlprog = matches[0][0]
                    scrapedtitle = matches[0][1]

                    date = scrapertools.find_single_match(chapter, '<time datetime="[^"]+" pubdate class="updated">(.*?) - [^<]+</time>')

                    # Añade al listado
                    itemlist.append(
                        Item(channel=channel,
                             action = 'play',
                             title = date.strip() + " - " + str(scrapedtitle).replace("&quot;", "'").replace("&#8220;", "").replace("&#8221;", "").replace('“', "").replace('”', "").strip(),
                             url = urlprog,
                             thumbnail = scrapedthumbnail,
                             server = channel,
                             folder = False
                        )
                    )

                except:
                    for line in sys.exc_info():
                        logger.error("tvalacarta.channels.8tv pager ERROR1: %s" % line)


        # Extrae el paginador para la página siguiente
        patron = "<a class="+"'"+"no_bg"+"'"+' href="([^"]+)">Següent</a>'
        urlpager = re.compile(patron,re.DOTALL).findall(data)
        #logger.info("URLPAGER: %s" % urlpager[0])

        if len(urlpager)>0 :
            next_page_item = Item(channel=channel,
                         action = 'loadprogram',
                         title = '>> Següent',
                         url = urlpager[0],
                         thumbnail = ''
                    )

            itemlist.append(next_page_item)
    except:
        for line in sys.exc_info():
            logger.error("tvalacarta.channels.8tv pager ERROR2: %s" % line)

    return itemlist


# Reproduce el item con server propio
def play(item):

    item.server = __channel__;
    itemlist = [item]

    return itemlist


# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    # Comprueba que la primera opción tenga algo
    items = mainlist(Item())
    section = loadsections(items[1])

    if len(section)==0:
        return False,"No hay videos en portada"

    section = loadprogram(items[4])

    if len(section)==0:
        return False,"No hay videos en 8aldia"

    return True,""
