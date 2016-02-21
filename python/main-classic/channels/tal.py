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
    itemlist.append( Item(channel=__channel__, title="Los más vistos" , url="http://tal.tv/es/" , action="ultimos" , extra="maisvistos", folder=True) )
    itemlist.append( Item(channel=__channel__, title="Lo más reciente" , url="http://tal.tv/es/" , action="ultimos" , extra="recentes", folder=True) )
    itemlist.append( Item(channel=__channel__, title="Series" , url="http://tal.tv/es/serie/" , action="series" , folder=True) )
    itemlist.append( Item(channel=__channel__, title="Por tema" , url="http://tal.tv/es/" , action="temas" , extra = "menuTemas" , folder=True) )
    itemlist.append( Item(channel=__channel__, title="Por país" , url="http://tal.tv/es/" , action="temas" , extra = "paises" , folder=True) )
    itemlist.append( Item(channel=__channel__, title="Por asociado" , url="http://tal.tv/es/" , action="temas", extra = "cedente" , folder=True) )
    return itemlist

def ultimos(item):
    logger.info("tvalacarta.channels.tal ultimos")    
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.find_single_match(data,'<nav id="'+item.extra+'">(.*?)</nav>')

    '''
    <a href="http://tal.tv/es/video/meta-2/" >
    <img width="236" height="135" src="http://tal.tv/wp-content/uploads/2011/10/P002585-236x135.jpg" class="attachment-webtv-video-thumb wp-post-image" alt="P002585" />                </a>
    <a class="titulo" href="http://tal.tv/es/video/meta-2/">META 2</a>
    <span class="play"></span>
    <span class="duracao">00:24:30</span>
    <span class="longline">El coleo de los cowboys de Meta y su típica danza joropo.</span>
    '''
    patron = '<a href="([^"]+)"[^<]+'
    patron += '<img width="\d+" height="\d+" src="([^"]+)"[^<]+</a>[^<]+'
    patron += '<a class="titulo" href="[^"]+">([^<]+)</a[^<]+'
    patron += '<span class="play"></span[^<]+'
    patron += '<span class="duracao">([^<]+)</span[^<]+'
    patron += '<span class="longline">([^<]+)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedthumbnail,scrapedtitle,duracion,scrapedplot in matches:
        title = scrapedtitle+" ("+duracion+")"
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = scrapedplot
        itemlist.append( Item(channel=__channel__, action="play", title=title, url=url, thumbnail=thumbnail, fanart=thumbnail, plot=plot, viewmode="movie_with_plot", folder=False))

    return itemlist

def temas(item):
    logger.info("tvalacarta.channels.tal temas")    
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    patron = '<nav id="'+item.extra+'(.*?)</nav>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if matches:
        data= matches[0]
    patron = '<a\s+href="([^"]+)[^>]+>([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl,scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        url = scrapedurl
        if not url.startswith("http://tal.tv/es"):
            url = url.replace("http://tal.tv/","http://tal.tv/es/")
        if url.startswith("http"):
            itemlist.append( Item(channel=__channel__, action="videos", title=title, url=url, thumbnail="",  folder=True))

    return itemlist

def series(item):
    logger.info("tvalacarta.channels.tal series")    
    itemlist = []

    '''
    <li>
    <a href="http://tal.tv/es/serie/al-natural/" >
    <img width="133" height="100" src="http://tal.tv/wp-content/uploads/2012/07/logo-serie-Al-Natural-133x100.jpg" class="attachment-serie-thumb wp-post-image" alt="logo-serie-Al-Natural" />              </a>
    <h3><a href="http://tal.tv/es/serie/al-natural/" ><p>Conservación de los recursos naturales, conciencia ante el medio ambiente y la realidad social y cultural de diversos pueblos de América Latina y el Caribe.</p>
    </a></h3>
    <div class="dados">
    <div class="wrap-dados">
    <div class="dados-content">
    <h4>AL NATURAL - AGUA EN…</h4>
    <span class="epsodios">8 episódios</span>                    <span class="pais panama">Panamá</span>
    </div><!-- .dados-content -->
    </div><!-- .wrap-dados -->
    </div><!-- .dados -->
    </li>
    '''
    data = scrapertools.cachePage(item.url)
    patron  = '<li[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img width="[^"]+" height="[^"]+" src="([^"]+)" class="[^"]+" alt="[^"]+"[^<]+</a[^<]+'
    patron += '<h3><a href="[^"]+"[^<]+<p>([^<]+)</p[^<]+'
    patron += '</a></h3[^<]+'
    patron += '<div class="dados"[^<]+'
    patron += '<div class="wrap-dados"[^<]+'
    patron += '<div class="dados-content"[^<]+'
    patron += '<h4>([^<]+)</h4[^<]+'
    patron += '<span class="epsodios">([^<]+)</span[^<]+'
    patron += '<span class="pais[^"]+">([^<]+)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl,scrapedthumbnail,scrapedplot,scrapedtitle,num_episodios,pais in matches:
        title = scrapedtitle+" ("+num_episodios+") ("+pais+")"
        url = scrapedurl
        thumbnail = scrapedthumbnail
        plot = scrapedplot
        itemlist.append( Item(channel=__channel__, action="episodios", title=title, url=url, thumbnail=thumbnail, plot=plot, folder=True))

    next_page_url = scrapertools.find_single_match(data,'<li><a href="([^"]+)" class="next">')
    if next_page_url!="":
        itemlist.append( Item(channel=__channel__, action="series", title=">> Página siguiente", url=urlparse.urljoin(item.url,next_page_url), thumbnail="",  folder=True))

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.tal episodios")    
    itemlist = []

    '''
    <ul class="related"><li ><a href="http://tal.tv/es/video/buscadores-de-la-armonia/"><img width="236" height="135" src="http://tal.tv/wp-content/uploads/2011/10/P000232-236x135.jpg" class="attachment-webtv-video-thumb wp-post-image" alt="P000232" /></a><a href="http://tal.tv/es/video/buscadores-de-la-armonia/" class="titulo">BUSCADORES DE LA ARMONIA</a>
    <span class="play"></span>
    <span class="duracao">00:25:55</span><span class="longline">Seres índigos y cristales: la evolución de la especie humana.</span></li><li ><a href="http://tal.tv/es/video/las-damas-gardelianas/"><img width="236" height="135" src="http://tal.tv/wp-content/uploads/2011/10/P001737-236x135.jpg" class="attachment-webtv-video-thumb wp-post-image" alt="P001737" /></a><a href="http://tal.tv/es/video/las-damas-gardelianas/" class="titulo">LAS DAMAS GARDELIANAS</a>
    <span class="play"></span>
    <span class="duracao">00:22:15</span><span class="longline">Fanatismo no tiene edad. Conozca al club de fans de Carlos Gardel.</span></li><li ><a href="http://tal.tv/es/video/a-favor-del-viento/"><img width="236" height="135" src="http://tal.tv/wp-content/uploads/2011/10/P000216-236x135.jpg" class="attachment-webtv-video-thumb wp-post-image" alt="P000216" /></a><a href="http://tal.tv/es/video/a-favor-del-viento/" class="titulo">A FAVOR DEL VIENTO</a>
    <span class="play"></span>
    <span class="duracao">00:25:00</span><span class="longline">Barriletes y cometas: juego de niños tomado en serio por muchachos.</span></li><li style=margin-right:0;><a href="http://tal.tv/es/video/enemigos-de-las-sustancias/"><img width="236" height="135" src="http://tal.tv/wp-content/uploads/2011/10/P000222-236x135.jpg" class="attachment-webtv-video-thumb wp-post-image" alt="P000222" /></a><a href="http://tal.tv/es/video/enemigos-de-las-sustancias/" class="titulo">ENEMIGOS DE LAS SUSTANCIAS</a>
    <span class="play"></span>
    <span class="duracao">00:25:00</span><span class="longline">La actitud straight edge: el gusto por el hardcore sin drogas.</span></li><li ><a href="http://tal.tv/es/video/las-ratas-de-asalto/"><img width="236" height="135" src="http://tal.tv/wp-content/uploads/2011/10/P000233-236x135.jpg" class="attachment-webtv-video-thumb wp-post-image" alt="P000233" /></a><a href="http://tal.tv/es/video/las-ratas-de-asalto/" class="titulo">LAS RATAS DE ASALTO</a>
    <span class="play"></span>
    <span class="duracao">00:22:30</span><span class="longline">Muchachos vestidos de guerra se realizan jugando paintball.</span></li><li ><a href="http://tal.tv/es/video/los-saltarines-urbanos/"><img width="236" height="135" src="http://tal.tv/wp-content/uploads/2011/10/P001739-236x135.jpg" class="attachment-webtv-video-thumb wp-post-image" alt="P001739" /></a><a href="http://tal.tv/es/video/los-saltarines-urbanos/" class="titulo">LOS SALTARINES URBANOS</a>
    <span class="play"></span>
    <span class="duracao">00:22:30</span><span class="longline">Encuentro nacional de pankour moviliza Buenos Aires.</span></li><li ><a href="http://tal.tv/es/video/guardianes-del-pasado/"><img width="236" height="135" src="http://tal.tv/wp-content/uploads/2011/10/P000217-236x135.jpg" class="attachment-webtv-video-thumb wp-post-image" alt="P000217" /></a><a href="http://tal.tv/es/video/guardianes-del-pasado/" class="titulo">GUARDIANES DEL PASADO</a>
    <span class="play"></span>
    <span class="duracao">00:24:15</span><span class="longline">Locos por Gordini. Jóvenes que todavía hoy veneran al Renault Gordini.</span></li></ul>      </div><!-- #programas -->

    </section>
    '''
    data = scrapertools.cachePage(item.url)
    data = scrapertools.find_single_match(data,'<ul class="related">(.*?)</ul>')
    patron  = '<li[^<]+'
    patron += '<a href="([^"]+)"><img width="[^"]+" height="[^"]+" src="([^"]+)" class="[^"]+" alt="[^"]+" /></a[^<]+'
    patron += '<a[^>]+>([^<]+)</a[^<]+'
    patron += '<span class="play"></span[^<]+'
    patron += '<span class="duracao">([^<]+)</span><span class="longline">([^<]+)</span></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl,scrapedthumbnail,scrapedtitle,duracion,scrapedplot in matches:
        title = scrapedtitle+" ("+duracion+")"
        url = scrapedurl
        thumbnail = scrapedthumbnail
        plot = scrapedplot
        itemlist.append( Item(channel=__channel__, action="play", title=title, url=url, thumbnail=thumbnail, plot=plot, folder=False))

    if len(itemlist)==0:
        itemlist = videos(item)

    return itemlist

def videos(item):
    logger.info("tvalacarta.channels.tal videos")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.find_single_match(data,'<section id="main-area">(.*?)</section>')

    patron = "<li(.*?)</li>"
    matches = re.compile(patron,re.DOTALL).findall(data)

    for match in matches:
        logger.info("tvalacarta.channels.tal videos match="+match)    
        '''
        <a href="http://tal.tv/es/video/payara-a-la-lena-palo-a-pique/" >
        <img width="134" height="77" src="http://tal.tv/wp-content/uploads/2011/10/P000949-134x77.jpg" class="attachment-video-thumb wp-post-image" alt="P000949" />            </a>
        <h3><a href="http://tal.tv/es/video/payara-a-la-lena-palo-a-pique/" >Recetas de pescados de la Amazonia venezolana.</a></h3>
        <div class="dados">
        <div class="wrap-dados">
        <div class="dados-content">
        <h4>PAYARA A LA LEÑA, PALO…</h4>
        <span class="duracao">00:23:40</span>
        <span class="pais venezuela">Venezuela</span>
        </div>
        </div>
        </div>
        '''
        duracion = scrapertools.find_single_match(match,'<span class="duracao">([^<]+)</span>')
        pais = scrapertools.find_single_match(match,'<span class="pais[^>]+>([^<]+)</span>')
        titulo = scrapertools.find_single_match(match,'<h4>([^<]+)</h4>')

        if titulo!="":
            title = titulo+" ("+duracion+") ("+pais+")"
            url = scrapertools.find_single_match(match,'<a href="([^"]+)"')
            thumbnail = scrapertools.find_single_match(match,'<img width="\d+" height="\d+" src="([^"]+)"')
            plot = scrapertools.find_single_match(match,'<h3><a[^>]+>([^<]+)</a></h3>')

            itemlist.append( Item(channel=__channel__, action="play", title=title, url=url, thumbnail=thumbnail, plot=plot, fanart=thumbnail, viewmode="movie_with_plot", folder=False))

    next_page_url = scrapertools.find_single_match(data,'<li><a href="([^"]+)" class="next">')
    if next_page_url!="":
        itemlist.append( Item(channel=__channel__, action="videos", title=">> Página siguiente", url=urlparse.urljoin(item.url,next_page_url), thumbnail="",  folder=True))

    return itemlist

def play(item):
    logger.info("tvalacarta.channels.tal play")    
    
    itemlist = []
    data = scrapertools.cachePage(item.url)
    video_id = scrapertools.find_single_match(data,'<iframe id="vzvd-(\d+)"')
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
