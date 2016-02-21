# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para kideos
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib,re

from core import logger
from core import scrapertools
from core.item import Item 

DEBUG = False
__channel__ = "kideos"

DEFAULT_HEADERS = []
DEFAULT_HEADERS.append(['User-Agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; es-ES; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12'])
DEFAULT_HEADERS.append(["Origin","http://www.kideos.com"])
DEFAULT_HEADERS.append(["Kodomo-Product","Kideos"])

URL_CANALES = "http://kodomo-production.inakalabs.com/api/categories?max_age=10&min_age=0"
URL_VIDEOS = "http://kodomo-production.inakalabs.com/api/films?featured=true&max_age=10&min_age=0"
#curl -v -H "" -H "Accept: application/json, text/plain, */*" -H "Kodomo-Product: Kideos" "http://kodomo-production.inakalabs.com/api/categories?max_age=10&min_age=0" > out.json

def isGeneric():
    return True

def read(url):
    return scrapertools.cache_page(url, headers=DEFAULT_HEADERS)

def mainlist(item):
    logger.info("tvalacarta.channels.kideos mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Vídeos destacados"   , action="episodios" , url=URL_VIDEOS, folder=True) )
    itemlist.append( Item(channel=__channel__, title="Canales"             , action="programas" , url=URL_CANALES , folder=True) )

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.kideos programas")
    itemlist = []
    
    # Descarga la lista de canales
    if item.url=="":
        item.url = URL_CANALES

    data = read(item.url)
    #logger.info("data="+data)
    '''
    "id":30,"name":"Featured","icon_url":"https://kodomo-inaka-production.s3.amazonaws.com/uploads/30/thumbnail_Featured_Star.png","color":"#0d9cf9","slug":"featured"
    '''
    patron  = '"id"\:(\d+),"name"\:"([^"]+)","icon_url"\:"([^"]+)","color"\:"([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,scrapedthumbnail,color in matches:
        title = scrapedtitle.strip()
        #http://kodomo-production.inakalabs.com/api/films?category_id=12&max_age=10&min_age=0&page=1&per_page=9
        url = "http://kodomo-production.inakalabs.com/api/films?category_id="+scrapedurl+"&max_age=10&min_age=0&page=1&per_page=9"
        thumbnail = scrapedthumbnail
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=__channel__, title=title , action="episodios" , url=url, thumbnail=thumbnail, plot=plot , show = title , folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.kideos episodios")
    itemlist = []
    
    # Descarga la lista de canales
    data = read(item.url)
    logger.info("data="+data)
    '''
    "id":7,
    "title":"Baby loves when Mom blows her nose",
    "description":"This baby is afraid of his mom when she blows her nose but then thinks its funny!  ",
    "slug":"baby-loves-when-mom-blows-her-nose",
    "product_specific_properties":{"min_age":2,"max_age":5},
    "video":{"source":"N9oxmRT2YWw","source_type":"youtube","length":"0:59"},
    "categories":[
        {"id":30,"name":"Featured","icon_url":"https://kodomo-inaka-production.s3.amazonaws.com/uploads/30/thumbnail_Featured_Star.png","color":"#0d9cf9","slug":"featured"},
        {"id":18,"name":"Cute LOL","icon_url":"https://kodomo-inaka-production.s3.amazonaws.com/uploads/18/thumbnail_Cute_Funny.png","color":"#942099","slug":"cute-lol"}],
    "platforms":[{"id":4,"name":"All"}]}
    '''
    patron  = '"id"\:(\d+),"title"\:"([^"]+)","description"\:"([^"]+)".*?"source"\:"([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,scrapedplot,youtube_id in matches:
        title = scrapedtitle
        url = "http://www.youtube.com/watch?v="+youtube_id
        thumbnail = "http://img.youtube.com/vi/"+youtube_id+"/mqdefault.jpg"
        plot = scrapedplot
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=__channel__, title=title , action="play" , server="youtube", url=url, thumbnail=thumbnail, fanart=thumbnail, plot=plot , show = item.show , viewmode="movie_with_plot", folder=False) )

    current_page = scrapertools.find_single_match(item.url,"\&page=(\d+)")
    if len(itemlist)>0 and current_page!="":
        next_page = str(int(current_page)+1)
        next_page_url = item.url.replace("&page="+current_page,"&page="+next_page)
        itemlist.append( Item(channel=__channel__, title=">> Página siguiente" , action="episodios" , url=next_page_url, thumbnail=item.thumbnail, plot=item.plot , show = item.show , folder=True) )

    return itemlist

def test():

    # Al entrar sale una lista de programas
    programas_items = mainlist(Item())
    if len(programas_items)==0:
        print "No devuelve programas"
        return False

    videos_items = episodios(programas_items[0])
    if len(videos_items)==1:
        print "No devuelve videos en "+programas_items[0].title
        return False

    return True