# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para cuatro
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import time
import random

try:
    from core import logger
    from core import scrapertools
    from core.item import Item
except:
    # En Plex Media server lo anterior no funciona...
    from Code.core import logger
    from Code.core import scrapertools
    from Code.core.item import Item

logger.info("[cuatro.py] init")

DEBUG = False
CHANNELNAME = "cuatro"

def isGeneric():
    return True

def mainlist(item):
    logger.info("[cuatro.py] mainlist")
    
    if item is None:
        # "2" es la portada
        item=Item(url="2")
    
    return programas(item)

def programas(item):
    logger.info("[cuatro.py] programas")
    itemlist = []

    # Descarga la página
    api_timestamp = int(time.time() * 1000)
    api_nonce = random.randint(1000000000,9999999999)
    data = scrapertools.cachePage("http://api.cuatro.webtv.flumotion.com/channel/%s/children?extended=1&api_referrer=ignore&api_nonce=%d&api_key=YxktBAUSh6EteWfxReGUu2KJSt4pjN79DnJvftgsvjurbrVj&api_timestamp=%d" % (item.url,api_nonce,api_timestamp))
    #logger.info(data)

    # Extrae las entradas
    '''
    {
    "campaign_id": 161, 
    "externalURL": "", 
    "description": "vídeos recién capturados de cuatro", 
    "background_url": "http://cuatro.media.webtv.flumotion.com/cuatro/oldimage/2010/8/24/128264873089_fondo-noticias-ok.jpg", 
    "rss_image_url": "http://cuatro.media.webtv.flumotion.com/cuatro/oldimage/2010/8/30/128316737767_podcast-rss-10.png", 
    "uri": "cuatro-10", 
    "publishDate": null, 
    "name": "cuatro +10'", 
    "num_children": 0, 
    "thumbnail_url": "http://cuatro.media.webtv.flumotion.com/cuatro/image/2011/2/17/cuatro10-canal-4d5d0c72.jpg", 
    "extra_field_list": [], 
    "all_tags": [
        "podcast"
    ], 
    "id": 88, 
    "creationDate": "2010-08-20 09:15:48", 
    "num_videos": 11, 
    "logo_url": "http://cuatro.media.webtv.flumotion.com/cuatro/oldimage/2010/8/30/128316696051_podcast-logo-10.png", 
    "unpublishDate": null
    },
    '''
    # Lo convierte a un diccionario estándar de Python
    data = data.replace("false","False").replace("true","True")
    data = data.replace("null","None")
    datadict = eval("("+data+")")
    
    for programa in datadict:
        scrapedtitle = programa['name'] #+" (%d vídeos)" % programa['num_videos']
        scrapedurl = str(programa['id'])
        scrapedthumbnail = programa['thumbnail_url']
        scrapedplot = programa['description']
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , show=scrapedtitle, category="programas", page=scrapedurl, folder=True) )
    
    return itemlist

def episodios(item):
    logger.info("[cuatro.py] episodios")
    itemlist = []

    # Descarga la página
    #http://api.cuatro.webtv.flumotion.com/channel/88/videos?extended=1&api_timestamp=1314976209&api_referrer=ignore&api_key=YxktBAUSh6EteWfxReGUu2KJSt4pjN79DnJvftgsvjurbrVj&api_nonce=1639739606
    api_timestamp = int(time.time() * 1000)
    api_nonce = random.randint(1000000000,9999999999)
    data = scrapertools.cachePage("http://api.cuatro.webtv.flumotion.com/channel/%s/videos?extended=1&api_timestamp=%d&api_referrer=ignore&api_key=YxktBAUSh6EteWfxReGUu2KJSt4pjN79DnJvftgsvjurbrVj&api_nonce=%d" % (item.url,api_timestamp,api_nonce))
    logger.info(data)

    # Extrae las entradas
    '''
    {
    "secure": 0, 
    "campaign": 89, 
    "uri": "modulos", 
    "duration": 2108, 
    "captions": [], 
    "id": 6390, 
    "title": "Módulos   ", 
    "extra_fields": [
        {
        "field_type": "LNK", 
        "order": 1, 
        "value": "http://www.cuatro.com/callejeros/ ", 
        "name": "Más sobre Callejeros"
        }, 
        {
        "field_type": "LNK", 
        "order": 2, 
        "value": "http://www.cuatro.com/callejeros-viajeros/", 
        "name": "También Callejeros Viajeros"
        }, 
        {
        "field_type": "META", 
        "order": 1, 
        "value": "", 
        "name": "Temporada"
        }, 
        {
        "field_type": "META", 
        "order": 2, 
        "value": "", 
        "name": "Capitulo"
        }, 
        {
        "field_type": "META", 
        "order": 3, 
        "value": "callejeros", 
        "name": "Canal"
        }
    ], 
    "tags": [
        "play4", 
        "reportajes", 
        "callejeros", 
        "programascompletos", 
        "modulos", 
        "playcuatro", 
        "cuatrotv"
    ], 
    "highlighted": 0, 
    "videoImage": 74027, 
    "unpublishDate": null, 
    "description": "Son simples módulos por fuera, pero por dentro se convierten, para sus dueños, en las viviendas de sus sueños…o de sus pesadillas. No te pierdas Callejeros. Módulos\n", 
    "embeddable": 1, 
    "public_url": "portada/callejeros", 
    "publishDate": "2011-05-06 21:45:00", 
    "credits": null, 
    "onAirDate": "2011-05-06 21:00:00", 
    "creationDate": "2011-05-05 10:37:14", 
    "average_rate": 0.0, 
    "ads_blocked": 0, 
    "total_rates": 0, 
    "thumbnail_url": "http://cuatro.media.webtv.flumotion.com/cuatro/image/2011/5/5/callejeros-modulos-86x66-4dc27ff9.jpg", 
    "livestream": 0, 
    "video_image_url": "http://cuatro.media.webtv.flumotion.com/cuatro/image/2011/5/5/callejeros-modulos-640x360-4dc28003.jpg"
    }, 
    '''
    # Lo convierte a un diccionario estándar de Python
    data = data.replace("false","False").replace("true","True")
    data = data.replace("null","None")
    datadict = eval("("+data+")")
    
    for episodio in datadict:
        #print episodio
        scrapedtitle = episodio['title']
        scrapedurl = "http://play.cuatro.com/directo/"+episodio['public_url']+"/ver/"+episodio['uri']
        scrapedthumbnail = episodio['video_image_url']
        scrapedplot = episodio['description']
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play2" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , page=scrapedurl, show=item.show, folder=False) )

    # Si el programa tiene subcategorias, las parsea ahora
    subitemlist = programas(item)
    for subitem in subitemlist:
        itemlist2 = episodios(subitem)
        for item2 in itemlist2:
            # Cambia el programa, las subcategorias no tienen el mismo
            item2.show = item.show
            itemlist.append(item2)

    return itemlist
