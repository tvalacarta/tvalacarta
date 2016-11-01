# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# tvalacarta 4
# Copyright 2015 tvalacarta@gmail.com
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
# This file is part of tvalacarta 4.
#
# tvalacarta 4 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tvalacarta 4 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tvalacarta 4.  If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------
# XBMC entry point
#------------------------------------------------------------
# Canal para Navarra TV
#------------------------------------------------------------

import urlparse,urllib,re

from core import logger
from core import scrapertools
from core.item import Item 

DEBUG = False
__channel__ = "navarratv"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.navarratv mainlist")

    item.url="http://www.natv.es/Alacarta"
    item.view="programs"
    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.navarratv programas")    

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    '''
    <div class="ImpactoBloque W50 H120 FranjaRoja Noticia2Col">
    <div class="ImpactoBloqueImagen W98" style="height: 150px;">
    <div class="ImpactoContenedorImagen" style="height: 150px; cursor: pointer; background-image: url('http://i.natv.es/imagenes/A82E542A-FD3D-485F-C933A8E7C294C438.JPG');" onclick="location.href='/AlaCarta/92C813D7-1676-E17B-1AB1E57E2065947C/Implicados';"/></div>
    </div>    
    <div class="ImpactoBloqueContenido W98">
    <h2><a href="/AlaCarta/92C813D7-1676-E17B-1AB1E57E2065947C/Implicados" class="TextoNeutro">Implicados</a></h2> 
    <p>Programa semanal que presenta el periodista Alejandro Palacios y que sirve para dar a conocer la labor de las personas que se implican por lograr una sociedad mejor.</p>
    </div>
    </div>
    '''
    patron  = '<div class="ImpactoBloque W50 H120 FranjaRoja[^<]+'
    patron += '<div class="ImpactoBloqueImagen[^<]+'
    patron += "<div class=\"ImpactoContenedorImagen\".*?url\('([^']+)'\)[^<]+</div[^<]+"
    patron += '</div[^<]+'
    patron += '<div class="ImpactoBloqueContenido[^<]+'
    patron += '<h2><a href="([^"]+)" class="TextoNeutro">([^<]+)</a></h2[^<]+'
    patron += '<p>([^<]*)</p>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedthumbnail,scrapedurl,scrapedtitle,scrapedplot in matches:
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapertools.safe_unicode(scrapedtitle).encode("utf-8").strip()
        plot = scrapedplot.strip()

        itemlist.append( Item(channel=__channel__, action="episodios", title=title, show=title, url=url, thumbnail=thumbnail, fanart=thumbnail, plot=plot, folder=True))

    return itemlist

def detalle_programa(item):
    return item

def episodios(item,load_all_pages=True):
    logger.info("tvalacarta.channels.navarratv episodios")    

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    '''
    <div class="Bloque2Noticias">
    <div class="ImpactoBloque W50 H120 FranjaRoja ">
    <div class="ImpactoBloqueImagen W98" style="height: 150px;">
    <div class="ImpactoContenedorImagen" style="height: 150px; cursor: pointer; background-image: url('https://i.ytimg.com/vi/RXBDpg7oduk/mqdefault.jpg');" onclick="location.href='/AlaCarta/92C813D7-1676-E17B-1AB1E57E2065947C/yt/RXBDpg7oduk/IMPLICADOS-18-DE-JUNIO-DE-2016';"/></div>
    </div>    
    <div class="ImpactoBloqueContenido W98">
    <h2><a href="/AlaCarta/92C813D7-1676-E17B-1AB1E57E2065947C/yt/RXBDpg7oduk/IMPLICADOS-18-DE-JUNIO-DE-2016" class="TextoNeutro">IMPLICADOS 18 DE JUNIO DE 2016</a></h2> 
    <p>IMPLICADOS 18 DE JUNIO DE 2016</p>
    </div>
    </div>
    <div class="W3"></div>  
    '''

    patron  = '<div class="Bloque2Noticias"[^<]+'
    patron += '<div class="ImpactoBloque W50 H120 FranjaRoja[^<]+'
    patron += '<div class="ImpactoBloqueImagen[^<]+'
    patron += "<div class=\"ImpactoContenedorImagen\".*?url\('([^']+)'\)[^<]+</div[^<]+"
    patron += '</div[^<]+'
    patron += '<div class="ImpactoBloqueContenido[^<]+'
    patron += '<h2><a href="([^"]+)" class="TextoNeutro">([^<]+)</a></h2[^<]+'
    patron += '<p>([^<]*)</p>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedthumbnail,scrapedurl,scrapedtitle,scrapedplot in matches:
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)

        yt_id = scrapertools.find_single_match(scrapedurl,"/yt/([^/]+)/")
        url = "https://www.youtube.com/watch?v="+yt_id
        title = scrapertools.safe_unicode(scrapedtitle).encode("utf-8").strip()
        plot = ""

        itemlist.append( Item(channel=__channel__, action="play", server="youtube", title=title, url=url, thumbnail=thumbnail, fanart=thumbnail, show=item.show, plot=plot, folder=True))

    return itemlist


# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    
    # Mainlist es la lista de programas
    programas_items = mainlist(Item())
    if len(programas_items)==0:
        print "No encuentra los programas"
        return False

    episodios_items = videos(programas_items[0])
    if len(episodios_items)==0:
        print "El programa '"+programas_items[0].title+"' no tiene episodios"
        return False

    return True
