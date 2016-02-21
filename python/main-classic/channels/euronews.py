# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal EURONEWS
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "euronews"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.euronews mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="English", action="categorias", url="http://www.euronews.com") )

    data = scrapertools.cache_page("http://www.euronews.com/")
    '''
    <option  dir="ltr" style="text-align:left" lang="en" value="http://www.euronews.com/">English</option>
    <option class="alt"  dir="ltr" style="text-align:left" lang="fr" value="http://fr.euronews.com/">Français</option>
    <option  dir="ltr" style="text-align:left" lang="de" value="http://de.euronews.com/">Deutsch</option>
    <option class="alt"  dir="ltr" style="text-align:left" lang="it" value="http://it.euronews.com/">Italiano</option>
    '''
    patron = '<option.*?value="(http\://[a-z]+\.euronews\.com/)">([^<]+)</option>'
    matches = re.findall(patron,data,re.DOTALL)
    for url,idioma in matches:
        itemlist.append( Item(channel=CHANNELNAME, title=idioma, action="categorias", url=url) )

    return itemlist

def categorias(item):
    logger.info("tvalacarta.euronews categorias")
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    
    # Enlace a "Programas"
    #<li class="menu-element-programs"><a title="Los Programas" href="/programas/">Los Programas</a></li>
    patron = '<li class="menu-element-programs"><a title="[^"]+" href="([^"]+)">([^<]+)</a>'
    matches = re.findall(patron,data,re.DOTALL)
    for url,titulo in matches:
        itemlist.append( Item(channel=CHANNELNAME, title=titulo, action="programas", url=urlparse.urljoin(item.url,url)) )

    itemlist.append( Item(channel=CHANNELNAME, title="", action="videos", url="") )

    # Restringe la búsqueda al bloque del menú de categorias
    data2 = scrapertools.get_match(data,'<ol id="categoryNav">(.*?)</ol>')
    '''
    <ol id="categoryNav">
    <li><a class="firstNavLink" href="/news/">News</a></li>
    <li><a href="/business/">Business</a></li>
    <li><a href="/sport/">Sport</a></li>
    <li><a href="/culture/">Culture</a></li>
    <li><a href="/nocomment/">no comment</a></li>
    <li><a href="/european-union/">European Affairs</a></li>
    <li><a href="/sci-tech/">Sci-tech</a></li>
    <li><a href="/travel/">Travel</a></li>
    <li><a href="/in-vogue/">In vogue</a></li>
    <li id="lastNavLink"><a href="/weather/">weather</a></li>    
    </ol>
    '''
    patron = '<li><a.*?href="([^"]+)">([^<]+)</a>'
    matches = re.findall(patron,data2,re.DOTALL)
    
    for url,titulo in matches:
        itemlist.append( Item(channel=CHANNELNAME, title=titulo, action="videos", url=urlparse.urljoin(item.url,url)) )

    itemlist.append( Item(channel=CHANNELNAME, title="", action="videos", url="") )

    # Restringe la búsqueda al bloque del menú por continentes
    data2 = scrapertools.get_match(data,'<ol class="lhsMenu">(.*?)</ol>')
    patron = '<li><a.*?href="([^"]+)">([^<]+)</a>'
    matches = re.findall(patron,data2,re.DOTALL)
    
    for url,titulo in matches:
        itemlist.append( Item(channel=CHANNELNAME, title=titulo, action="videos", url=urlparse.urljoin(item.url,url)) )

    return itemlist

def programas(item):
    logger.info("tvalacarta.euronews programas")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    '''
    <li id="europe-weekly">
    <a class="imgWrap" href="/programas/europe-weekly/" title="europe weekly">
    <img src="http://static.euronews.com/articles/programs/160x90_europe-weekly.jpg" alt="europe weekly"  title="europe weekly" />
    <div>
    <h2  class="programTitle">europe weekly</h2>
    <p  class="artTitle">europe Weekly Euronews le ofrece la última hora de la actualidad económica, financiera y empresarial a nivel internacional, con los eventos de la semana.</p>
    </div>
    <br style="clear:both;"/>
    </a>
    </li>
    '''
    patron  = '<li[^<]+'
    patron += '<a class="imgWrap" href="([^"]+)" title="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '<div[^<]+'
    patron += '<h2[^<]+</h2[^<]+'
    patron += '<p\s+class="artTitle">([^<]+)</p'

    matches = re.findall(patron,data,re.DOTALL)
    
    for url,titulo,thumbnail,plot in matches:
        itemlist.append( Item(channel=CHANNELNAME, title=titulo, action="videos", url=urlparse.urljoin(item.url,url), thumbnail=thumbnail, plot=plot, viewmode="movie_with_plot", fanart=thumbnail, folder=True) )

    return itemlist

def videos(item):
    logger.info("tvalacarta.euronews videos")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    logger.info("data="+data)

    patron  = '<a class="imgLink[^"]+" title="([^"]+)" href="([^"]+)"[^<]+'
    patron += '<span class="iconPlay"><\!-- KEEP IT FULL --></span[^<]+'
    patron += '<img src="([^"]+)"'
    matches = re.findall(patron,data,re.DOTALL)

    for scrapedtitle,scrapedurl,scrapedthumbnail in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append( Item(channel=CHANNELNAME, action="play", title=title, url=url, thumbnail=thumbnail, plot=plot, folder=False) )

    patron  = '<a class="imgLink[^"]+" title="([^"]+)" href="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)"'
    matches = re.findall(patron,data,re.DOTALL)

    for scrapedtitle,scrapedurl,scrapedthumbnail in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append( Item(channel=CHANNELNAME, action="play", title=title, url=url, thumbnail=thumbnail, plot=plot, folder=False) )

    #<a href="/nocomment/2013/12/16/sudafrica-moteros-dicen-adios-a-mandela/" class="topStory"><img src="http://static.euronews.com/images_news/img_287X161_1612-south-africa-motors.jpg?1387188241" alt="Sudáfrica: moteros dicen adiós a Mandela" width="287" height="161" />
    patron  = '<a href="(/nocomment[^"]+)" class="topStory"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.findall(patron,data,re.DOTALL)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapedtitle
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append( Item(channel=CHANNELNAME, action="play", title=title, url=url, thumbnail=thumbnail, plot=plot, folder=False) )


    return itemlist

def play(item):
    logger.info("tvalacarta.euronews play")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    #               sources: [{file: "http://video.euronews.com/flv/nocomment/nocom-131220_NCSU_007A0-2112-_VI.flv?1387617304", label: "320p"}],
    #http://video.euronews.com/flv/nocomment/nocom-131220_NCSU_007A0-2112-_VI.flv?1387617304
    patron  = 'file\:\s*"([^"]+)"'
    matches = re.findall(patron,data,re.DOTALL)
    for url in matches:
        mediaurl = url
        itemlist.append( Item(channel=CHANNELNAME, title=item.title, action="play", url=mediaurl, thumbnail=item.thumbnail) )

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    idiomas_items = mainlist(Item())
    categorias_items = categorias(idiomas_items[0])

    # Comprueba que salgan programas
    for categoria_item in categorias_items:
        if categoria_item.action=="programas":
            programas_items = programas(categoria_item)
            if len(programas_items)==0:
                print "No hay programas"
                return False

    # Busca una lista de videos no vacia
    for categoria_item in categorias_items:
        if categoria_item.action=="videos":
            videos_items = videos(categoria_item)
            if len(videos_items)>0:
                return True

    print "No hay videos en ninguna categoria"

    return False
