# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Levante TV (Valencia)
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "levantetv"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.levantetv mainlist")

    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.levantetv canal")

    item.url = "http://alacarta.levantetv.es/categories"

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data,'<ul class="category-list">(.*?)</ul')
    
    '''
    <ul class="category-list">
        <li>
            <a class="underline-hover  " href="/categories/bona-nit">BONA NIT</a>
        </li><li>
            <a class="underline-hover  " href="/categories/comarca">Comarca</a>
        </li><li>
    '''

    # Extrae las zonas de los programas
    patron  = '<li[^<]+<a class="[^"]+" href="([^"]+)">([^<]+)</a>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url,scrapedurl)+"/latest"
        thumbnail = ""
        plot = ""

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="episodios", show=title, folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.levantetv episodios")

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)

    '''
    <li>
    <a href="/media/els-nostres-majors-28-de-marc" title="Els nostres majors 28 de març">
    <strong class="grid-title">Els nostres majors 28 de març</strong>
    <span class="thumb-wrap">
    <img src="/images/media/11446s.jpg" width="128" height="72" alt="" />
    </span><br />
    <span class="grid-desc mcore-text"></span><br />
    <span class="grid-meta mcore-text">
    <span class="meta meta-likes" title="19 Les gustan">19 <span>Les gustan</span></span>
    <span class="meta meta-views" title="297 Vistas">297 <span>Vistas</span></span>
    </span>
    </a>
    </li>
    '''

    # Extrae las zonas de los videos
    patron  = '<li[^<]+'
    patron += '<a href="([^"]+)" title="([^"]+)"[^<]+'
    patron += '<strong class="grid-title"[^<]+</strong[^<]+'
    patron += '<span class="thumb-wrap"[^<]+'
    patron += '<img src="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = ""

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="play", server="levantetv", show=item.show, folder=False) )

    next_page_url = scrapertools.find_single_match(data,'<a href="([^"]+)" class="mcore-btn mcore-btn-grey mcore-pager-link"><span><stron[^<]+</strong></span></a[^<]+</div>')
    if next_page_url!="":
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page_url), action="episodios", show=item.show, folder=True) )

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    # Comprueba que la primera opción tenga algo
    categorias_items = mainlist(Item())
    programas_items = programas(categorias_items[0])
    episodios_items = episodios(programas_items[0])

    if len(episodios_items)>0:
        return True

    return False