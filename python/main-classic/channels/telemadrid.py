# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para telemadrid
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "telemadrid"
MAIN_URL = "http://www.telemadrid.es/tv_a_la_carta/listado_de_programas/"

def isGeneric():
    return True

def mainlist(item):
    logger.info("[telemadrid.py] mainlist")

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(MAIN_URL)
    
    # Limita la página al bloque con las categorías
    data = scrapertools.get_match(data,'<div class="anclasProgramas">(.*?)</div>')

    # Extrae las categorias
    patron = '<h2><a href="/tv_a_la_carta/listado_de_programas\#(portProgr[^"]+)">([^<]+)</a></h2>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = scrapedurl
        thumbnail = ""
        
        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url,  thumbnail=thumbnail , action="programas" , folder=True) )

    return itemlist

def programas(item):
    logger.info("[telemadrid.py] programas")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(MAIN_URL)
    
    # Limita la página al bloque con la categoría elegida (va en la url)
    data = scrapertools.get_match(data,'<div id="'+item.url+'">(.*?)</ul>')

    '''
    <li class="views-row views-row-1 views-row-odd views-row-first">    
    <a href="/tv_a_la_carta/listado_de_programas/566" class="imagen">
    <img src="http://www.telemadrid.es/sites/default/files/images/logo_micamara_2012.destacado.jpg" alt="Logo Mi Cámara y Yo 2012" title="Logo Mi Cámara y Yo 2012"  class="image image-destacado " width="128" height="106" /></a>    
    <a href="/tv_a_la_carta/listado_de_programas/566" class="titulo">Mi cámara y yo</a> <p><P>Cada semana, un reportero del programa recorre la Comunidad de Madrid con una minicámara, interfiriendo lo menos posible en el relato, para ofrecer la parte más desconocida y más cercana de la realidad, tratando siempre de ver las cosas desde otro ángulo, entrando con la cámara en la vida cotidiana de los espectadores.
    '''
    
    # Extrae programas
    patron  = '<li[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)"[^<]+</a[^<]+'
    patron += '<a[^>]+>([^<]+)</a[^<]+<p>(.*?)</li'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedplot in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(MAIN_URL,scrapedurl)
        thumbnail = scrapedthumbnail
        plot = scrapedplot
        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url,  thumbnail=thumbnail , action="episodios" , show = item.title , folder=True) )

    return itemlist

def episodios(item):
    logger.info("[telemadrid.py] episodios")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    
    # Limita la página al bloque donde estan los episodios
    data = scrapertools.get_match(data,'<div class="tituloTodosProgramas">(.*?)</ul>')
    
    # Extrae episodios
    '''
    <li class="views-row views-row-4 views-row-even">
    <a href="/?q=programas/madrilenos-por-el-mundo/madrilenos-por-el-mundo-washington-dc" class="playerIco imagen">
    <img src="http://www.telemadrid.es/sites/default/files/images/thumb_mxm_C0156_20121119_1353361585428.destacado.png" alt="Madrileños por el Mundo: Washington D.C." title="Madrileños por el Mundo: Washington D.C."  class="image image-destacado " width="150" height="106" /></a>
    <a href="/?q=programas/madrilenos-por-el-mundo/madrilenos-por-el-mundo-washington-dc" class="titulo">Madrileños por el Mundo: Washington D.C.</a>
    <p class="fechaEmision"><span class="date-display-single">19.11.2012</span></p></li>
    '''
    patron  = '<li[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)"[^<]+</a[^<]+'
    patron += '<a[^>]+>([^<]+)</a[^<]+<p class="fechaEmision">(.*?)</p>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedplot in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail
        plot = scrapertools.htmlclean(scrapedplot)
        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url,  thumbnail=thumbnail , action="play" , server="telemadrid", show = item.title , folder=False) )

    return itemlist

def get_video_detail(item):
    logger.info("[telemadrid.py] get_video_detail")

    data = scrapertools.cache_page(item.url)
    
    data = scrapertools.cache_page("http://pydowntv2.appspot.com/api?url="+page_url)
    item.thumbnail = scrapertools.get_match(data,'"url_img"\: "([^"]+)"')
    item.plot = scrapertools.get_match(data,'"descs"\: \["([^"]+)"\]')

    return item

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    # Comprueba que la primera opción tenga algo
    categorias_items = mainlist(Item())
    programas_items = programas(categorias_items[0])
    episodios_items = episodios(programas_items[0])

    if len(episodios_items)>0:
        return True

    return False