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

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.telemadrid mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Telemadrid" , url="http://www.telemadrid.es/programas/directorio_programas" , action="canal", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="laOtra" , url="http://www.telemadrid.es/laotra/directorio_programas" , action="canal", folder=True) )

    return itemlist

def canal(item):
    logger.info("tvalacarta.channels.telemadrid canal")

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)
    
    '''
    <li class="views-row views-row-6 views-row-even">
    <a href="/talcomoson" class="imagen">
    <img src="http://www.telemadrid.es/sites/default/files/images/logo_talcomoson.jpg" alt="logo_talcomoson" title="logo_talcomoson"  class="image image-_original " width="230" height="190" />
    </a>   
    <a href="/talcomoson" class="titulo">Tal como Son</a>
    <p><p>Un reportero de <B>Tal Como Son</b> pasa un día en la vida de un famoso. En cada programa aparecen cuatro personajes relevantes de la vida social. Personalidades del mundo de la cultura, la empresa, la aristocracia, el deporte. Conocemos aspectos desconocidos para el telespectador de la vida de estas celebridades de universos muy distintos.</p></p>
    </li>
    '''

    '''
    <a class="playerIco imagen" href="http://www.telemadrid.es/ruta179" >
    <img width="142" height="106" class="image image-destacado" title="Ruta 179" alt="Ruta 179 visita Piñuecar y Gandullas" src="http://www.telemadrid.es/sites/default/files/Images2015/pinuecar_gandullas.jpg">
    </a>
    <a class="titulo" href="http://www.telemadrid.es/ruta179" >Ruta 179</a>
    <span>Nos vamos de ruta por la Comunidad de Madrid</span>                       
    </li>
    '''

    # Extrae las zonas de los programas
    patron = '<li class="views-row(.*?</li>)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for bloque in matches:
        title = scrapertools.find_single_match(bloque,'<a href="[^"]+" class="titulo">([^<]+)</a>')

        # El titulo puede venir de dos formas (en telemadrid y en laotra)
        if title=="":
            title = scrapertools.find_single_match(bloque,'<a class="titulo" href="[^"]+" >([^<]+)</a>')
            url = scrapertools.find_single_match(bloque,'<a class="titulo" href="([^"]+)"')
            thumbnail = scrapertools.find_single_match(bloque,'<img.*?src="([^"]+)"')
            plot = scrapertools.find_single_match(bloque,'<a class="titulo" href="[^"]+" >[^<]+</a>(.*?)</li>')
        else:
            url = scrapertools.find_single_match(bloque,'<a href="([^"]+)" class="titulo">')
            thumbnail = scrapertools.find_single_match(bloque,'<img src="([^"]+)"')
            plot = scrapertools.find_single_match(bloque,'<a href="[^"]+" class="titulo">[^<]+</a>(.*?)</li>')

        # URL absoluta
        url = urlparse.urljoin(item.url,url)

        # Limpia el argumento
        plot = scrapertools.htmlclean(plot)
        plot = plot.replace("693 056 799","")
        plot = plot.replace("680 116 002","")

        if title!="":
            itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="episodios", show=title, folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.telemadrid episodios")

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)

    '''
    <li class="views-row views-row-2 views-row-even"> 
    <a href="/programas/mi-camara-y-yo/mi-camara-y-yo-el-rastro" class="playerIco imagen">
    <img src="http://www.telemadrid.es/sites/default/files/Images2016/thumb_P10000315_C0007HDP0_20170412_1492466104083.foto.png" alt="Mi cámara y yo: El Rastro" title="Mi cámara y yo: El Rastro"  class="image image-foto " width="300" height="169" />
    </a> 
    <a href="/programas/mi-camara-y-yo/mi-camara-y-yo-el-rastro" class="titulo">Mi cámara y yo: El Rastro</a>   
    <span class="date-display-single">17.04.2017</span></li>
    '''

    # Intenta filtrar por "programas completos", si no saca todo
    bloque = scrapertools.find_single_match(data,'<div class="headerView[^<]+<h3 class="titulo">Los programas</h3>(.*)</div[^<]+</div')
    if bloque!="":
        data = bloque

    # Extrae las zonas de los videos
    patron = '<li class="views-row(.*?</li>)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for bloque in matches:
        title = scrapertools.find_single_match(bloque,'<a href="[^"]+" class="titulo">([^<]+)</a>')
        url = scrapertools.find_single_match(bloque,'<a href="([^"]+)" class="titulo">')
        thumbnail = scrapertools.find_single_match(bloque,'<img src="([^"]+)"')
        plot = scrapertools.find_single_match(bloque,'<a href="[^"]+" class="titulo">[^<]+</a>(.*?)</li>')

        # URL absoluta
        url = urlparse.urljoin(item.url,url)

        # Limpia el argumento
        plot = scrapertools.htmlclean(plot)
        plot = plot.replace("693 056 799","")
        plot = plot.replace("680 116 002","")

        if title!="":
            itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="play", server="telemadrid", show=item.show, folder=False) )

    next_page_url = scrapertools.find_single_match(data,'<li class="pager-next"><a href="([^"]+)" title="Ir a la p')
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