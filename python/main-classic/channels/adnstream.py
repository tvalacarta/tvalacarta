# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para ADNStream
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import config
from core import scrapertools
from core.item import Item

DEBUG = config.get_setting("debug")
CHANNELNAME = "adnstream"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.adnstream mainlist")

    itemlist = []
    data = scrapertools.cache_page("http://www.adnstream.com")
    data = scrapertools.get_match(data,'<div class="botones" id="canales"(.*?)</div>')

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)" title="[^"]+">([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.strip()
        #/canal/Documentales/
        url = urlparse.urljoin("http://www.adnstream.com",scrapedurl)
        thumbnail = "http://www.adnstream.com/img/"+scrapedurl.replace("/canal/","canales/")[:-1]+"_w320.jpg"
        
        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url,  thumbnail=thumbnail , action="subcanales" , viewmode="movie", folder=True) )

    return itemlist

def subcanales(item):
    logger.info("tvalacarta.channels.adnstream subcanales")

    itemlist = []
    data = scrapertools.cache_page(item.url)
    patron  = '<a class="captura" href="([^"]+)">[^>]+'
    patron += '<img width="\d+" height="\d+" src="([^"]+)"[^<]+'
    patron += '</a>[^<]+'
    patron += '<h3>[^<]+'
    patron += '<a[^>]+>([^>]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail.replace("w160","w320")

        if url=="http://www.adnstream.com/canal/BRBplay/":
            itemlist.append( Item(channel=CHANNELNAME, title="BRBplay en español" , url="http://www.adnstream.com/canal/BRBplay-en-espanol/",  thumbnail=thumbnail , action="subcanales" , show = item.title , folder=True) )
            itemlist.append( Item(channel=CHANNELNAME, title="BRBplay en inglés" , url="http://www.adnstream.com/canal/BRBplay-en-ingles/",  thumbnail=thumbnail , action="subcanales" , show = item.title , folder=True) )
        else:
            itemlist.append( Item(channel=CHANNELNAME, title=title , url=url,  thumbnail=thumbnail , action="subcanales" , viewmode="movie", show = item.title , folder=True) )

    if len(itemlist)==0:
        itemlist = videos(item)

    return itemlist

def videos(item):
    logger.info("tvalacarta.channels.adnstream videos")

    itemlist = []
    data = scrapertools.cache_page(item.url)
    '''
    <a class="captura" href="/video/zmeXyuLsiC/Pasion-de-Gavilanes-Ep006">
    <span>&nbsp;</span>
    <img width="160" height="120" src="http://46.4.33.243/static/thbs/z/zmeXyuLsiC_w160.jpg" alt="Pasión de Gavilanes - Ep006" title="Pasión de Gavilanes - Ep006" />
    </a>
    </span>
    <h3>
    <a href="/video/zmeXyuLsiC/Pasion-de-Gavilanes-Ep006" title="Pasión de Gavilanes - Ep006">Pasión de Gavilanes - Ep006</a>
    '''
    patron  = '<a class="captura" href="([^"]+)">[^>]+'
    patron += '<span>[^<]+</span>[^>]+'
    patron += '<img width="\d+" height="\d+" src="([^"]+)"[^<]+'
    patron += '</a>[^<]+'
    patron += '</span>[^<]+'
    patron += '<h3>[^<]+'
    patron += '<a[^>]+>([^>]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail
        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url,  thumbnail=thumbnail , action="play" , server="adnstream", show = item.show , folder=False) )

    # Página siguiente
    # <a href="/canal/Pasion-de-Gavilanes/2" class="flecha">Next &gt;</a>
    patron = '<a href="([^"]+)" class="flecha">Next .gt.</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)>0:
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , url=urlparse.urljoin(item.url,matches[0]), action="videos" , show = item.show , folder=True) )

    return itemlist

def play(item):

    item.server="adnstream";
    itemlist = [item]

    return itemlist

def get_video_detail(item):
    
    data = scrapertools.cache_page(item.url)
    item.title = scrapertools.get_match(data,'<meta name="title" content="([^"]+)" />')
    item.plot = scrapertools.get_match(data,'<meta name="description" content="(.*?)" rel="canonical" />')
    
    return item

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    # El canal tiene estructura canal -> subcanal -> videos
    canales = mainlist(Item())
    if len(canales)==0:
        return False

    subcanales = mainlist(canales[1])
    if len(subcanales)==0:
        return False

    videos = mainlist(Item(url="http://www.adnstream.com/canal/Dartacan/"))
    if len(videos)==0:
        return False
    
    return bien
