# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para TAL
# creado por rsantaella
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "tal"
__category__ = "F"
__type__ = "generic"
__title__ = "tal"
__language__ = "ES"
__creationdate__ = "20130319"
__vfanart__ = "http://tal.tv/wp-content/themes/tal.tv/images/bg-body1.png"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.tal mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Español" , url="" , action="menu", extra="es", folder=True) )
    itemlist.append( Item(channel=__channel__, title="Português" , url="" , action="menu", extra="pt", folder=True) )

    return itemlist

def menu(item):
    logger.info("tvalacarta.channels.tal menu")

    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Más vistos" , url="http://tal.tv/"+item.extra+"/mais-vistos/" , action="episodios", folder=True) )
    itemlist.append( Item(channel=__channel__, title="Novedades" , url="http://tal.tv/"+item.extra+"/novidades/" , action="episodios" , extra="recentes", folder=True) )
    itemlist.append( Item(channel=__channel__, title="Series" , url="http://tal.tv/"+item.extra+"/serie/" , action="series" , folder=True) )
    itemlist.append( Item(channel=__channel__, title="Por tema" , url="http://tal.tv/"+item.extra+"/" , action="temas" , extra = "tema" , folder=True) )
    itemlist.append( Item(channel=__channel__, title="Por país" , url="http://tal.tv/"+item.extra+"/" , action="temas" , extra = "pais" , folder=True) )
    return itemlist

def temas(item):
    logger.info("tvalacarta.channels.tal temas")    
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    patron = '<div class="sub '+item.extra+'(.*?)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if matches:
        data= matches[0]
    patron = '<a\s+href="([^"]+)[^>]+>([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl,scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        url = scrapedurl
        itemlist.append( Item(channel=__channel__, action="episodios", title=title, url=url, thumbnail="",  folder=True))

    return itemlist

def series(item):
    logger.info("tvalacarta.channels.tal series")    
    itemlist = []

    '''
    <li>
    <a href="http://tal.tv/es/serie/autores-en-vivo/">
    <div class="imagem">
    <img width="237" height="177" src="http://tal.tv/wp-content/uploads/2013/12/AUTORES-EN-VIVO-237x177.jpg" class="attachment-serie-header size-serie-header wp-post-image" alt="AUTORES EN VIVO" srcset="http://tal.tv/wp-content/uploads/2013/12/AUTORES-EN-VIVO-237x177.jpg 237w, http://tal.tv/wp-content/uploads/2013/12/AUTORES-EN-VIVO-133x100.jpg 133w" sizes="(max-width: 237px) 100vw, 237px" />                   
    </div>

    <h2>AUTORES EN VIVO</h2>
    <p>Ciclo de shows de autores uruguayos impulsionado por la Asociación General de Autores de...</p>
    <div class="info-serie">
    <div class="pais">
    <i class="flag uruguai"></i>
    <span>Uruguay</span>
    </div>
    <div class="qtd">
    <i class="fa fa-television"></i>
    <span class="epsodios">9 episódios</span>                        </div>
    </div>
    </a>
    </li>
    '''
    data = scrapertools.cachePage(item.url)
    patron  = '<li[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<div class="imagem"[^<]+'
    patron += '<img width="[^"]+" height="[^"]+" src="([^"]+)"[^<]+'
    patron += '</div[^<]+'
    patron += '<h2>([^<]+)</h2[^<]+'
    patron += '<p>([^<]+)</p[^<]+'
    patron += '<div class="info-serie"[^<]+'
    patron += '<div class="pais"[^<]+'
    patron += '<i class="flag[^<]+</i[^<]+'
    patron += '<span>([^<]+)</span'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedplot,pais in matches:
        title = scrapedtitle+" ("+pais+")"
        url = scrapedurl
        thumbnail = scrapedthumbnail
        plot = scrapedplot
        itemlist.append( Item(channel=__channel__, action="episodios", title=title, url=url, thumbnail=thumbnail, fanart=thumbnail, plot=plot, viewmode="movie_with_plot", folder=True))

    next_page_url = scrapertools.find_single_match(data,'<li><a href="([^"]+)" class="next"')
    if next_page_url!="":
        itemlist.append( Item(channel=__channel__, action="series", title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page_url) ,  folder=True) )    

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.tal episodios")    
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    logger.info("tvalacarta.channels.tal data="+data)    

    '''
    <li>
    <a href="http://tal.tv/es/video/los-paraguayos/" >
    <div class="imagem">
    <img width="300" height="171" src="http://tal.tv/wp-content/uploads/2011/10/P001769.jpg" class="attachment-webtv-300 size-webtv-300 wp-post-image" alt="P001769" srcset="http://tal.tv/wp-content/uploads/2011/10/P001769.jpg 482w, http://tal.tv/wp-content/uploads/2011/10/P001769-300x170.jpg 300w, http://tal.tv/wp-content/uploads/2011/10/P001769-134x77.jpg 134w, http://tal.tv/wp-content/uploads/2011/10/P001769-236x135.jpg 236w" sizes="(max-width: 300px) 100vw, 300px" />                        
    <div class="info">
    <i class="flag paraguai"></i>
    <small class="duracao"> <i class="fa fa-clock-o"></i> 00:54:00</small>
    </div>
    </div>
    <h2>LOS PARAGUAYOS</h2>
    <span>De los orígenes guaraníes al Paraguay contemporáneo: una historia de contrastes.</span>
    </a>
    </li>
    '''
    patron  = '<li[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<div class="imagem"[^<]+'
    patron += '<img width="\d+" height="\d+" src="([^"]+)"[^<]+'
    patron += '<div class="info"[^<]+'
    patron += '<i class="flag ([^"]+)"></i[^<]+'
    patron += '<small class="duracao"> <i class="fa fa-clock-o"></i>([^<]+)</small[^<]+'
    patron += '</div[^<]+'
    patron += '</div[^<]+'
    patron += '<h2>([^<]+)</h2[^<]+'
    patron += '<span>([^<]+)</span'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedthumbnail,pais,duracion,scrapedtitle,scrapedplot in matches:
        title = scrapertools.htmlclean( scrapedtitle+" ("+pais+")"+" ("+duracion+")" )
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = scrapedplot
        itemlist.append( Item(channel=__channel__, action="play", title=title, url=url, thumbnail=thumbnail, fanart=thumbnail, plot=plot, viewmode="movie_with_plot", folder=False))

    #<li><a href="http://tal.tv/es/mais-vistos/page/2/" class="next">&gt;</a>
    next_page_url = scrapertools.find_single_match(data,'<li><a href="([^"]+)" class="next"')
    if next_page_url!="":
        itemlist.append( Item(channel=__channel__, action="episodios", title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page_url) ,  folder=True) )    

    return itemlist

def play(item):
    logger.info("tvalacarta.channels.tal play")    
    
    itemlist = []
    data = scrapertools.cachePage(item.url)
    video_id = scrapertools.find_single_match(data,'<iframe id="vzvd-(\d+)"')

    #http://view.vzaar.com/586105/video
    mediaurl = "http://view.vzaar.com/"+video_id+"/video"    
    itemlist.append( Item(channel=__channel__, action="play",  server="directo",  title=item.title, url=mediaurl, folder=False))

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    # Todas las opciones tienen que tener algo
    categorias_items = mainlist(Item())

    # Lista de series
    if len(categorias_items)==0:
        print "No hay categorias"
        return False

    videos_items = videos(categorias_items[0])
    if len(videos_items)==0:
        print "La categoria "+categorias_items[0].title+" no tiene videos"
        return False

    mediaurl_items = play(videos_items[0])
    if len(mediaurl_items)==0:
        print "Error al averiguar la URL del primer episodio de "+series_items[0].title
        return False

    return True
