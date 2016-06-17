# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para DiscoveryMax
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import re, urllib

from core import logger
from core import scrapertools
from core import config
from core.item import Item
from servers import servertools

logger.info("tvalacarta.channels.discoverymax init")

DEBUG = False
CHANNELNAME = "discoverymax"


def isGeneric():
    return True


def mainlist(item):
    logger.info("tvalacarta.channels.discoverymax mainlist")
    thumbnail = "http://media.tvalacarta.info/tvalacarta/squares/discoverymax.png"
    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Novedades", action="novedades", url="http://www.discoverymax.marca.com/player/", thumbnail=thumbnail, folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Programas", action="programas", url="http://www.discoverymax.marca.com/wp-content/plugins/dni_plugin_core/ajax.php?action=dni_listing_items_filter&letter=&page=1&id=6667aa&post_id=1075&view_type=grid", thumbnail=thumbnail, folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Categorías", action="cat", url="http://www.discoverymax.marca.com/", thumbnail=thumbnail, folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Avances", action="episodios", url="http://www.discoverymax.marca.com/avances/", thumbnail=thumbnail, folder=True) )
    return itemlist

def novedades(item):
    logger.info("tvalacarta.channels.discoverymax novedades")

    itemlist = []
    data = scrapertools.cache_page(item.url).replace("\n","")

    listcat = scrapertools.find_multiple_matches(data, '<a href="#".*?data="([^"]+)".*?<p>([^<]+)</p>')
    dict = {}
    for key, value in listcat:
        dict[key] = value
    patron = '<div\s+data="([^"]+)"(.*?)<div class="dni-video-playlist-page-controls-bottom">'
    bloque = scrapertools.find_multiple_matches(data, patron)
    for title, content in bloque:
        titulo = "[COLOR yellow]       ****"+dict[title]+"****[/COLOR]"
        patron = '<div class="dni-video-playlist-thumb-box.*?<a href="([^"]+)".*?'
        patron += '<img src="([^"]+)".*?<h3 data-content=.*?>([^<]+)<.*?'
        patron += '<p class="desc".*?>([^<]+)<'
        matches = scrapertools.find_multiple_matches(content, patron)
        extra = len(matches)+1
        if "kodi" in config.get_platform(): action = "move"
        else: action = ""
        itemlist.append( Item(channel=CHANNELNAME, title=titulo, action=action, url="", thumbnail=item.thumbnail, fanart=item.fanart, extra=str(extra),folder=False) )
        for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot in matches:
            scrapedurl = item.url + scrapedurl
            itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle, action="play", url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, fanart=scrapedthumbnail, viewmode="list", folder=False) )

    return itemlist

def cat(item):
    logger.info("tvalacarta.channels.discoverymax cat")

    itemlist = []
    data = scrapertools.cache_page(item.url).replace("\n","")

    patron = '<ul class="sub-menu">(.*?)</ul>'
    bloque = scrapertools.find_single_match(data, patron)
    patron = '<a href="([^"]+)"><span>([^<]+)</span>'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.unescape(scrapedtitle)
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle, action="programascat", url=scrapedurl, thumbnail=item.thumbnail, viewmode="list", folder=True) )

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.discoverymax programas")

    itemlist = []
    if item.title == "Programas":
        itemlist.append( Item(channel=CHANNELNAME, title="[COLOR gold][B]>> Lista A-Z[/B][/COLOR]", action="alfabetico", url="http://www.discoverymax.marca.com/player/#id=6667aa&view_type=list", thumbnail="", folder=True) )
    data = scrapertools.cache_page(item.url).replace("\\","").replace("u00","\\u00")

    if scrapertools.find_single_match(data, '"items_count":(\d+)') == "0":
        itemlist.append(Item(channel=CHANNELNAME, title="Sin contenido", action="", url="", thumbnail="", folder=False))
        return itemlist
    
    patron = '<a href="([^"]+)".*?src="([^"]+)".*?<h3>([^<]+)</h3>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.decode('unicode_escape').encode('utf8')
        scrapedthumbnail = scrapedthumbnail.decode('unicode_escape').encode('utf8')
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle, action="episodios", url=scrapedurl, thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, show=scrapedtitle, folder=True) )

    total_pages = int(scrapertools.find_single_match(data, '"total_pages":(\d+)'))
    current_page = int(scrapertools.find_single_match(data, '"current_page":"([^"]+)"'))

    if current_page < total_pages:
        url = re.sub(r'page=(\d+)',"page="+str(current_page+1), item.url)
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente", action="programas", url=url, thumbnail="", folder=True) )
    return itemlist

def programascat(item):
    logger.info("tvalacarta.channels.discoverymax programascat")

    itemlist = []
    data = scrapertools.cache_page(item.url).replace("\n","")

    patron = '<section class="pagetype-show_homepage">.*?<a href="(.*?/series/.*?/.*?/).*?'
    patron += '.*?src="([^"]+)".*?<h3 class="item-title">([^<]+)<.*?'
    patron += '<p class="item-description">([^<]+)<'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot in matches:
        scrapedurl += "episodios-completos/"
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle, action="episodios", url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, fanart=scrapedthumbnail, folder=True) )
    return itemlist

def alfabetico(item):
    logger.info("tvalacarta.channels.discoverymax alfabetico")

    itemlist = []
    data = scrapertools.cache_page(item.url).replace("\n","")
    patron = '<h3 class="list-block-letter">(.*?)</h3>(.*?)(?:<div id=|</section>)'
    bloque = scrapertools.find_multiple_matches(data, patron)
    for title, content in bloque:
        titulo = "[COLOR yellow]       ****"+title+"****[/COLOR]"
        patron = '<a href="([^"]+)".*?<h3>([^<]+)<'
        matches = scrapertools.find_multiple_matches(content, patron)
        extra = len(matches)+1
        if "kodi" in config.get_platform(): action = "move"
        else: action = ""
        itemlist.append( Item(channel=CHANNELNAME, title=titulo, action=action, url="", thumbnail=item.thumbnail, fanart=item.fanart, extra=str(extra),folder=False) )
        for scrapedurl, scrapedtitle in matches:
            itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle, action="episodios", url=scrapedurl, thumbnail=item.thumbnail, fanart=item.fanart, folder=True) )

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.url.rsplit("/",2)[0]).replace("\n","")
    item.plot = scrapertools.find_single_match(data, '<div class="cfct-mod-content">(.*?)</div>')
    item.plot = scrapertools.htmlclean(item.plot)

    return item

def episodios(item):
    logger.info("tvalacarta.channels.discoverymax episodios")

    itemlist = []
    fanart = item.fanart
    clips = False
    if item.title != "Avances":
        data = scrapertools.cache_page(item.url.rsplit("/",2)[0]).replace("\n","")
        sinopsis = scrapertools.find_single_match(data, '<div class="cfct-mod-content">(.*?)</div>')
        sinopsis = scrapertools.htmlclean(sinopsis)
        fanart =  scrapertools.find_single_match(data, '<div class="dni-image ">.*?src="([^"]+)"')
        if "kodi" in config.get_platform(): action = "sinopsis"
        else: action = ""
        itemlist.append( Item(channel=CHANNELNAME, title="[COLOR yellow]Sinopsis[/COLOR]", action=action, url="", thumbnail=fanart, plot=sinopsis, fanart=fanart, folder=False) )
        if "<span>Clips</span>" in data and item.title != "[COLOR red]>> Clips de vídeo[/COLOR]":
            clips = True
            url_clips = scrapertools.find_single_match(data, '<a href="([^"]+)"><span>Clips</span>')

    try:
        data = scrapertools.downloadpageGzip(item.url).replace("\n","")
    except:
        data = scrapertools.cache_page(item.url.rsplit("/",2)[0]).replace("\n","")


    patron = '<div class="dni-video-playlist-thumb-box.*?<a href="([^"]+)".*?'
    patron += '<img src="([^"]+)".*?<h3 data-content=.*?>([^<]+)<.*?'
    patron += '<p class="desc".*?>([^<]+)<'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot in matches:
        scrapedurl = item.url + scrapedurl
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle, action="play", url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, fanart=fanart, show=item.show, folder=False) )

    if len(itemlist) < 2:
        itemlist.append( Item(channel=CHANNELNAME, title="No hay episodios completos disponibles", action="", url="", thumbnail=fanart, plot=sinopsis, fanart=fanart, folder=False) )
    if clips:
        itemlist.append( Item(channel=CHANNELNAME, title="[COLOR red]>> Clips de vídeo[/COLOR]", action="episodios", url=url_clips, thumbnail=fanart, plot=sinopsis, fanart=fanart, folder=True) )
    return itemlist

def move(item):
    import xbmc, xbmcgui
    item_focus = item.extra
    wnd = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    id = wnd.getFocusId()
    return xbmc.executebuiltin('Control.Move('+str(id)+','+item_focus+')')

def sinopsis(item):
    import xbmc
    return xbmc.executebuiltin('Action(Info)')
    

def play(item):
    logger.info("tvalacarta.channels.discoverymax play")
    itemlist = []
    data = scrapertools.cache_page(item.url).replace("\n","")
    url = url_brightcove(item.url.rsplit("#")[1], data)
    itemlist.append( Item(channel=CHANNELNAME, title="", action="play", url=url, server="discoverymax", thumbnail=item.thumbnail, plot=item.plot, folder=False) )

    return itemlist

def url_brightcove(videoplayer, data):
    bloque = scrapertools.find_single_match(data, '(<object class="BrightcoveExperience">.*?</object>)')
    order_params = ['playerID','playerKey']
    params = ""
    for i in range(0, len(order_params)):
        patron = '<param name="'+order_params[i]+'" value="([^"]+)"'
        match = scrapertools.find_single_match(bloque, patron)
        params += "&"+order_params[i]+"="+match
    url = "http://c.brightcove.com/services/viewer/federated_f9?"+params+"&@videoPlayer="+videoplayer
    return url
    