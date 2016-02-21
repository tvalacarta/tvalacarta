# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Telefe
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse
import urllib
import re
import traceback

from core import logger
from core import scrapertools
from core import jsontools
from core.item import Item

DEBUG = True
CHANNELNAME = "telefe"
MAIN_URL = "http://telefe.com/capitulos-completos/"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.telefe mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Últimos episodios añadidos" , action="videos" , thumbnail = "" , url = MAIN_URL))
    itemlist.extend(programas(item))

    return itemlist

def programas(item):
    logger.info("tvalacarta.telefe programas")
    
    itemlist = []

    '''
    <select id="programSearchCombo" style="display:none">
    <option id="0">Todos los programas</option>
    <option id="3133" value="3133">AM</option>
    <option id="6598" value="6598">Casados con hijos</option>
    '''

    headers = []
    headers.append(["Accept","text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"])
    headers.append(["Accept-Encoding","gzip,deflate"])
    headers.append(["Accept-Language","es-ES,es;q=0.8,en;q=0.6"])
    headers.append(["Connection","keep-alive"])
    headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36"])

    data = scrapertools.cache_page(MAIN_URL,headers=headers)
    data = scrapertools.find_single_match(data,'<select id="programSearchCombo"[^<]+<optio[^>]+>Todos los programas</option>(.*?)</select>')

    patron  = '<option id="\d+" value="(\d+)">([^<]+)</option>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        url = "http://telefe.com/capitulos-completos/?s=&layout=list&programa="+scrapedurl
        thumbnail = ""
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="videos" , url=url, thumbnail=thumbnail, plot=plot , show=scrapedtitle, folder=True) )

    itemlist = sorted(itemlist, key=lambda Item: Item.title)

    return itemlist

def videos(item):
    logger.info("tvalacarta.telefe videos")

    '''
    <div id='307218' class='large-4 small-12 column'>
    <div class='row'>
    <div class='b_search__result_item'>
    <a href='http://telefe.com/viudas-e-hijos-del-rock-roll/viudas-e-hijos-del-rock-roll-capitulo-123-(26-03-2015)/'>
    <div class='small-12 columns'>
    <div class='img-overlay-back'>
    <div class='badge-over-photo'>
    <img src='http://static.cdn.telefe.com/media/15220361/ortega-viudas_main.jpg?v=20150331124047000' style='border-color:#FF0810'/>
    <div class='badge-ribbon'>
    <div class='badge' style='background-color:#FF0810; color: white'>
    <p>Viudas e Hijos del Rock &amp; Roll</p>
    </div>
    </div>
    </div>
    </div>
    </div>
    <div class='small-12 columns'>
    <h5>Viudas e Hijos del Rock &amp; Roll - Cap&#237;tulo 123 (26-03-2015)</h5>
    <p>
    <span class='color-gray'>Emitido el 26 de marzo de 2015</span>

    </p>
    <p>Sandra admite qui&#233;n es el padre de su hijo.</p>
    </div>
    </a>
    </div>
    </div>
    </div>
    '''
    
    itemlist=[]
    headers = []
    headers.append(["Accept","text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"])
    headers.append(["Accept-Encoding","gzip,deflate"])
    headers.append(["Accept-Language","es-ES,es;q=0.8,en;q=0.6"])
    headers.append(["Connection","keep-alive"])
    headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36"])
    data = scrapertools.cache_page(item.url,headers=headers)
    patron  = "<div id='\d+' class='large-4 small-12 column'[^<]+"
    patron += "<div class='row'[^<]+"
    patron += "<div class='b_search__result_item'[^<]+"
    patron += "<a href='([^']+)'[^<]+"
    patron += "<div class='small-12 columns'[^<]+"
    patron += "<div class='img-overlay-back'[^<]+"
    patron += "<div class='badge-over-photo'[^<]+"
    patron += "<img src='([^']+)'[^<]+"
    patron += "<div class='badge-ribbon'[^<]+"
    patron += "<div[^<]+"
    patron += "<p>([^<]+)</p[^<]+"
    patron += "</div[^<]+"
    patron += "</div[^<]+"
    patron += "</div[^<]+"
    patron += "</div[^<]+"
    patron += "</div[^<]+"
    patron += "<div class='small-12 columns'[^<]+"
    patron += "<h5>([^<]+)</h5[^<]+"
    patron += "<p[^<]+<span[^<]+</span[^<]+</p[^<]+"
    patron += "<p>([^<]+)</p>"

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,show,scrapedtitle,scrapedplot in matches:
        title = scrapertools.htmlclean(show + ": " + scrapedtitle)
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = scrapertools.htmlclean(scrapedplot).strip()

        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="play" , server="telefe", url=url, thumbnail=thumbnail, fanart=thumbnail, plot=plot , show=show, folder=False) )

    try:
        current_page = scrapertools.find_single_match(data,'<input type="hidden" id="pageNumber" value="(\d+)">')
        next_page = str(int(current_page)+1)
        if "page=" in item.url:
            next_page_url = re.compile("page=\d+",re.DOTALL).sub("page="+next_page,item.url)
        else:
            if "?" in item.url:
                next_page_url = item.url+"&page="+next_page
            else:
                next_page_url = item.url+"?page="+next_page
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , action="videos" , url=next_page_url , folder=True ) )
    except:
        logger.info(traceback.format_exc())

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    
    # El canal tiene estructura programas -> episodios -> play
    items_programas = programas(Item())
    if len(items_programas)==0:
        print "No hay programas"
        return False

    # Ahora recorre los programas hasta encontrar vídeos en alguno
    for item_programa in items_programas:
        print "Verificando "+item_programa.title
        items_videos = videos(item_programa)
        if len(items_videos)>0:
            return True

    print "No hay videos en ningún programa"
    return False
