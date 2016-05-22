# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para TVN (Chile)
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import logger
from core import config
from core import scrapertools
from core.item import Item

DEBUG = True
CHANNELNAME = "tvn"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.tvn mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Programas"  , action="programas" , url="http://www.tvn.cl/programas", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Teleseries" , action="programas" , url="http://www.tvn.cl/teleseries", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Cultura"    , action="programas" , url="http://www.tvn.cl/cultura", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Especiales" , action="programas" , url="http://www.tvn.cl/especiales", folder=True) )

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.tvn programas")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    patron = '<ul class="nav_videos_destacados">(.*?)</ul>'
    bloques = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(bloques)

    for bloque in bloques:

        '''
        <li id='comcont11808009_1'>
        <a href="http://www.tvn.cl/programas/kunga/" >
        <img alt="Kunga" src="http://www.tvn.cl/incoming/afiche-kungapng-1852994/ALTERNATES/w620h450/Afiche-Kunga.png" />
        <div class="nav_videos_destacados_txt">
        <span>Sábado 22:30 horas</span>
        <h3>Kunga</h3>
        <p>Actitud Animal</p>
        '''
        '''
        <li id='comcont11807952_6'>
        <a href="http://www.tvn.cl/programas/mientrastanto/" >
        <img alt="Mientras Tanto" src="http://www.tvn.cl/incoming/afiche-mientrastantopng-1853001/ALTERNATES/w620h450/Afiche-MientrasTanto.png" />
        <div class="nav_videos_destacados_txt">
        <span></span>
        <h3>Mientras Tanto</h3>
        <p>#MientrasTantoTVN</p>
        </div>
        </a>
        </li>
        '''

        patron  = '<li[^<]+'
        patron += '<a href="([^"]+)"[^<]+'
        patron += '<img alt="[^"]+" src="([^"]+)"[^<]+'
        patron += '<div class="nav_videos_destacados_txt"[^<]+'
        patron += '<span>[^<]*</span[^<]+'
        patron += '<h3>([^<]+)</h3[^<]+'
        patron += '<p>([^<]*)</p>'
        matches = re.compile(patron,re.DOTALL).findall(bloque)
        if DEBUG: scrapertools.printMatches(matches)

        for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedplot in matches:
            title = scrapedtitle.strip()
            thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
            plot = scrapedplot
            url = urlparse.urljoin(item.url,scrapedurl)
            if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
            itemlist.append( Item( channel=item.channel , title=title , action="episodios" , url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=True ) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.tvn episodios")
    
    itemlist=parse_episodios(item,item.url)
    itemlist.extend( parse_episodios( item,urlparse.urljoin(item.url,"capitulos") ) )

    return itemlist

def parse_episodios(item,url):
    logger.info("tvalacarta.channels.tvn parse_episodios")

    itemlist = []
    data = scrapertools.cache_page(url)
    '''
    <figure id='comcont11979605_3'>
    <a href="http://www.tvn.cl/programas/oncecomida/capitulos/capitulo-17-once-comida-2018064" >
    <img class="img-responsive" alt="¡¿Quién espera la guagua?!" src="http://www.tvn.cl/incoming/once_comida_guaguajpg-2018072/ALTERNATES/w620h450/Once_Comida_Guagua.jpg" />
    </a>
    <div class="typeContent">
    <p><i class="fa fa-play-circle-o"></i></p>
    </div>
    <figcaption>
    <a href="http://www.tvn.cl/programas/oncecomida/capitulos/capitulo-17-once-comida-2018064" >
    <span>Capítulo 20 - Martes 17 de mayo</span>
    <h2>¡¿Quién espera la guagua?!</h2>
    <p>Una gran confusión invadió a la familia Iglesias. Mateo cree que Daniela está embarazada, Rodolfo c...</p>
    </a>
    </figcaption>
    </figure>
    '''
    patron  = '<figure id=[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img class="img-responsive" alt="[^"]+" src="([^"]+)"[^<]+'
    patron += '</a[^<]+'
    patron += '<div class="typeContent"[^<]+'
    patron += '<p><i[^<]+</i></p[^<]+'
    patron += '</div[^<]+'
    patron += '<figcaptio[^<]+'
    patron += '<a[^<]+'
    patron += '<span>([^<]+)</span[^<]+'
    patron += '<h2>([^<]+)</h2[^<]+'
    patron += '<p>([^<]+)</p>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedtitle2,scrapedplot in matches:
        title = scrapedtitle.strip()+" - "+scrapedtitle2.strip()
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = scrapedplot
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="play" , server="tvn", url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=False ) )

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    
    # El canal tiene estructura
    items_mainlist = mainlist(Item())
    items_programas = []

    # Todas las opciones del menu tienen que tener algo
    for item_mainlist in items_mainlist:
        exec "itemlist="+item_mainlist.action+"(item_mainlist)"
    
        if len(itemlist)==0:
            print "La sección '"+item_mainlist.title+"' no devuelve nada"
            return False

        items_programas = itemlist

    # Ahora recorre los programas hasta encontrar vídeos en alguno
    for item_programa in items_programas:
        print "Verificando "+item_programa.title
        items_episodios = episodios(item_programa)

        if len(items_episodios)>0:
            return True

    print "No hay videos en ningún programa"
    return False
