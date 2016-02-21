# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para boing.es
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import config
from core import logger
from core import scrapertools
from core.item import Item

DEBUG = config.get_setting("debug")
CHANNELNAME = "boing"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.boing mainlist")

    #itemlist = []
    #itemlist.append( Item(channel=CHANNELNAME, title="Últimos vídeos añadidos" , url="http://www.boing.es/videos" , action="episodios" , folder=True) )
    #itemlist.append( Item(channel=CHANNELNAME, title="Todas las series" , url="http://www.boing.es/series?order=title&sort=asc" , action="series" , folder=True) )

    item.url = "http://www.boing.es/videos"
    return episodios(item)

def series(item):
    logger.info("tvalacarta.channels.boing series")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    #logger.info(data)

    # Extrae las series
    '''
    <div class="pic"><div class="pic2"><div class="pic3"><a href="/serie/chowder" class="imagecache imagecache-130x73 imagecache-linked imagecache-130x73_linked"><img src="http://www.boing.es/sites/default/files/imagecache/130x73/chowder.jpg" alt="" title=""  class="imagecache imagecache-130x73" width="130" height="73" /></a></div></div></div>
    
    <div class="clear"></div>
    <div class="stars"><form action="/series?order=title&amp;sort=asc"  accept-charset="UTF-8" method="post" id="fivestar-custom-widget-26" class="fivestar-widget">
    <div><div class="fivestar-form-vote-813 clear-block"><input type="hidden" name="content_type" id="edit-content-type-26" value="node"  />
    <input type="hidden" name="content_id" id="edit-content-id-26" value="813"  />
    <div class="fivestar-form-item  fivestar-average-stars"><div class="form-item" id="edit-vote-52-wrapper">
    <span class='edit-vote-52-design'><span class='form-item-value-design1'><span class='form-item-value-design2'><span class='form-item-value-design3'> <input type="hidden" name="vote_count" id="edit-vote-count-26" value="0"  />
    <input type="hidden" name="vote_average" id="edit-vote-average-26" value="67.2237"  />
    <input type="hidden" name="auto_submit_path" id="edit-auto-submit-path-26" value="/fivestar/vote/node/813/vote"  class="fivestar-path" />
    <select name="vote" class="form-select" id="edit-vote-53" ><option value="-">Select rating</option><option value="20">Give it 1/5</option><option value="40">Give it 2/5</option><option value="60">Give it 3/5</option><option value="80" selected="selected">Give it 4/5</option><option value="100">Give it 5/5</option></select><input type="hidden" name="auto_submit_token" id="edit-auto-submit-token-26" value="56e73589059273a3c5fe1a8abc137a87"  class="fivestar-token" />
    
    </span></span></span></span></div>
    </div><input type="hidden" name="destination" id="edit-destination-26" value="series"  />
    <input type="submit" name="op" id="edit-fivestar-submit-26" value="Rate"  class="form-submit fivestar-submit" />
    <input type="hidden" name="form_build_id" id="form-7afce4746464c15152c61b751ad73da5" value="form-7afce4746464c15152c61b751ad73da5"  />
    <input type="hidden" name="form_id" id="edit-fivestar-custom-widget-26" value="fivestar_custom_widget"  />
    </div>
    </div></form></div>
    <div class="title"><a href="/serie/chowder">Chowder</a></div>
    
    <div class="sin">¿Quién dijo que cocinar es aburrido? La cocina de Chowder...</div>
    '''
    patron  = '<div class="pic"><div class="pic2"><div class="pic3"><a href="([^"]+)"[^<]+<img src="([^"]+)".*?'
    patron += '<div class="title"><a href="[^"]+">([^<]+)</a></div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    
    itemlist = []
    destacadas = 4
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        destacadas = destacadas - 1
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        if destacadas>=0:
            logger.info("ignorando, es de la caja de destacadas")
        else:
            itemlist.append( Item(channel=item.channel, title=scrapedtitle , action="episodios" , url=urlparse.urljoin(item.url,scrapedurl), thumbnail=scrapedthumbnail , show = scrapedtitle, folder=True) )
    
    #<li class="pager-next"><a href="/series?page=1&amp;order=title&amp;sort=asc" title="Ir a la página siguiente" class="active">siguiente
    patron = '<li class="pager-next"><a href="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    if len(matches)>0:
        itemlist.extend( series(Item(channel=item.channel, title="Página siguiente >>" , action="series" , url=urlparse.urljoin(item.url,matches[0].replace("&amp;","&")), folder=True) ) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.boing episodios")

    # Descarga la página
    #http://www.boing.es/serie/hora-de-aventuras
    #http://www.boing.es/videos/hora-de-aventuras
    data = scrapertools.cachePage(item.url.replace("/serie/","/videos/"))
    #logger.info(data)
    bloque = scrapertools.get_match(data,'<div class="Contenedor100">(.*?)<\!-- \/Contenedor100 -->',1)
    logger.info(str(bloque))

    # Extrae los videos
    '''
    <div class="pic"><div class="pic2"><div class="pic3">
    <a href="/serie/ninjago-maestros-del-spinjitzu/video/el-que-es-mordido-esta-en-peligro" class="imagecache imagecache-130x73 imagecache-linked imagecache-130x73_linked"><img src="http://www.boing.es/sites/default/files/imagecache/130x73/once_bitten.jpg" alt="" title=""  class="imagecache imagecache-130x73" width="130" height="73" /></a>                       
    </div></div></div>
    <div class="stars"><form action="/videos"  accept-charset="UTF-8" method="post" id="fivestar-custom-widget" class="fivestar-widget">
    <div><div class="fivestar-form-vote-102378 clear-block"><input type="hidden" name="content_type" id="edit-content-type" value="node"  />
    <input type="hidden" name="content_id" id="edit-content-id" value="102378"  />
    <div class="fivestar-form-item  fivestar-average-stars"><div class="form-item" id="edit-vote-wrapper">
    <input type="hidden" name="vote_count" id="edit-vote-count" value="0"  />
    <input type="hidden" name="vote_average" id="edit-vote-average" value="88.5714"  />
    <input type="hidden" name="auto_submit_path" id="edit-auto-submit-path" value="/fivestar/vote/node/102378/vote"  class="fivestar-path" />
    <select name="vote" class="form-select" id="edit-vote-1" ><option value="-">Select rating</option><option value="20">Give it 1/5</option><option value="40">Give it 2/5</option><option value="60">Give it 3/5</option><option value="80">Give it 4/5</option><option value="100" selected="selected">Give it 5/5</option></select><input type="hidden" name="auto_submit_token" id="edit-auto-submit-token" value="b8a094b5f4a56d752822bb55d0f3b99c"  class="fivestar-token" />
    </div>
    </div><input type="hidden" name="destination" id="edit-destination" value="videos"  />
    <input type="submit" name="op" id="edit-fivestar-submit" value="Rate"  class="form-submit fivestar-submit" />
    <input type="hidden" name="form_build_id" id="form-NGhpOchfYw6teS0LnyS0m4aGdHV0zd6oTgcFnHXdKwY" value="form-NGhpOchfYw6teS0LnyS0m4aGdHV0zd6oTgcFnHXdKwY"  />
    <input type="hidden" name="form_id" id="edit-fivestar-custom-widget" value="fivestar_custom_widget"  />
    </div>
    </div></form></div>
    <div class="series"><a href="/serie/ninjago-maestros-del-spinjitzu">Ninjago: maestros del Spinjitzu</a></div>
    <div class="title"><a href="/serie/ninjago-maestros-del-spinjitzu/video/el-que-es-mordido-esta-en-peligro">El que es mordido, está en peligro</a></div>
    '''
    patron  = '<div class="pic3"[^<]+'
    patron += '<a href="([^"]+)"[^<]+<img.*?src="([^"]+)".*?'
    patron += '<div class="series">(.*?)</div[^<]+'
    patron += '<div class="title"><a[^>]+>([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)
    #if DEBUG: scrapertools.printMatches(matches)

    if len(matches)==0:
        patron  = '<div class="pic3"[^<]+'
        patron += '<a href="([^"]+)"[^<]+<img src="([^"]+)".*?'
        patron += '<div class="series">(.*?)</div[^<]+'
        patron += '<div class="title"><a[^>]+>([^<]+)</a>'
        matches = re.compile(patron,re.DOTALL).findall(bloque)
        scrapertools.printMatches(matches)
        #if DEBUG: scrapertools.printMatches(matches)

    itemlist = []
    for scrapedurl,scrapedthumbnail,scrapedshow,scrapedtitle in matches:
        title = scrapedtitle
        if scrapedshow!="":
            title = scrapertools.find_single_match(scrapedshow,'<a[^>]+>([^<]+)</a>') + " - " + title
        if (DEBUG): logger.info("title=["+title+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        url = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="play", server="boing" , url=url, thumbnail=scrapedthumbnail, page=url, show = item.show, folder=False) )

    next_page = scrapertools.find_single_match(data,'<li class="pager-next"><a href="([^"]+)"')
    if next_page!="":
        itemlist.append( Item(channel=item.channel, title=">> Página siguiente" , action="episodios" , url=urlparse.urljoin(item.url,next_page), folder=True) )

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    # El canal tiene estructura programas -> episodios -> play
    programas_list = mainlist(Item())
    if len(programas_list)==0:
        return False

    for programa in programas_list:
        if programa.title=="Be Boing":
            episodios_list = episodios(programa)
            if len(episodios_list)==0:
                return False

    return bien