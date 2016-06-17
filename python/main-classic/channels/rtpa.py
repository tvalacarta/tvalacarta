# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para rtpa
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import config
from core import logger
from core import scrapertools
from core import jsontools
from core.item import Item

DEBUG = config.get_setting("debug")
CHANNELNAME = "rtpa"
PROGRAMAS_URL = "http://www.rtpa.es/json/vod_programas.json"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.rtpa mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Últimos vídeos añadidos" , url="http://www.rtpa.es/json/vod_parrilla_8.json" , action="novedades" , folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Programas actuales (con sinopsis)" , url="http://www.rtpa.es/json/programas_actuales_tpa.json" , action="programas_actuales" , folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Todos los programas" , url=PROGRAMAS_URL , action="programas" , folder=True) )

    return itemlist

def novedades(item):
    logger.info("tvalacarta.channels.rtpa novedades")

    itemlist = []

    data = scrapertools.cache_page(item.url)
    json_object = jsontools.load_json(data)
    #logger.info("json_object="+repr(json_object))

    for vod in json_object["VOD"]:
        title = vod["nombre_programa"]
        if vod["titulo"]!="":
            title = title + " - " + vod["titulo"]
        
        # http://www.rtpa.es/video:Caballos%20de%20metal_551396652766.html
        url = "http://www.rtpa.es/video:"+urllib.quote(vod["nombre_programa"])+"_"+vod["id_generado"]+".html"

        thumbnail = urllib.quote(vod["url_imagen"]).replace("//","/").replace("http%3A/","http://")
        plot = vod["sinopsis"]
        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url,  thumbnail=thumbnail , plot=plot, server="rtpa", action="play" , show = item.title , folder=False) )

    return itemlist

def programas_actuales(item):
    logger.info("tvalacarta.channels.rtpa programas_actuales")

    itemlist = []

    data = scrapertools.cache_page(item.url)
    json_object = jsontools.load_json(data)
    #logger.info("json_object="+repr(json_object))
    #logger.info("VOD="+repr(json_object["VOD"]))

    for vodlist in json_object["programas"]:
        
        for vod in vodlist:
            title = vod["nombre"]

            # http://www.rtpa.es/programa:LA%20QUINTANA%20DE%20POLA_1329394981.html
            #url = "http://www.rtpa.es/programa:"+urllib.quote(vod["nombre_programa"])+"_"+vod["id_programa"]+".html"

            # http://www.rtpa.es/api/muestra_json_vod.php?id_programa=1293185502
            url = "http://www.rtpa.es/api/muestra_json_vod.php?id_programa="+vod["id_generado"]
            thumbnail = urllib.quote(vod["imagen"]).replace("//","/").replace("http%3A/","http://")
            plot = scrapertools.htmlclean(vod["sinopsis"])
            itemlist.append( Item(channel=CHANNELNAME, title=title , url=url,  thumbnail=thumbnail , plot=plot, fanart=thumbnail, action="episodios" , show = item.title , viewmode="movie_with_plot", folder=True) )

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.rtpa programas")

    itemlist = []

    if item.url=="":
        item.url=PROGRAMAS_URL

    data = scrapertools.cache_page(item.url)
    json_object = jsontools.load_json(data)
    #logger.info("json_object="+repr(json_object))
    #logger.info("VOD="+repr(json_object["VOD"]))

    for vodlist in json_object["VOD"]:
        
        for vod in vodlist:
            title = vod["nombre_programa"]

            # http://www.rtpa.es/programa:LA%20QUINTANA%20DE%20POLA_1329394981.html
            #url = "http://www.rtpa.es/programa:"+urllib.quote(vod["nombre_programa"])+"_"+vod["id_programa"]+".html"

            # http://www.rtpa.es/api/muestra_json_vod.php?id_programa=1293185502
            url = "http://www.rtpa.es/api/muestra_json_vod.php?id_programa="+vod["id_programa"]
            thumbnail = urllib.quote(vod["url_imagen"]).replace("//","/").replace("http%3A/","http://")
            plot = ""
            # http://www.rtpa.es/programa:CONEXI%C3%B3N%20SALUDABLE_1372402706.html
            page_url = "http://www.rtpa.es/tpa-programa-todos:"+urllib.quote(vod["nombre_programa"])+"_"+vod["id_programa"]+".html"
            itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, page=page_url, thumbnail=thumbnail , plot=plot, action="episodios" , show = title , viewmode="movie", folder=True) )

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.page)

    item.plot = scrapertools.find_single_match(data,'<article class="span8"[^<]+<div class="contenido_noticia">(.*?)</div>')
    item.plot = scrapertools.htmlclean(item.plot).strip()

    item.thumbnail = scrapertools.find_single_match(data,'<img src="([^"]+)" alt="" class="img-det-not">')

    #item.title = scrapertools.find_single_match(data,'<article class="span8"[^<]+<h2>([^<]+)</h2>')

    return item

def episodios(item):
    logger.info("tvalacarta.channels.rtpa episodios")
    itemlist = []

    if "&fin=" not in item.url:
        item.url = item.url + "&fin=1000"

    data = scrapertools.cache_page(item.url)
    json_object = jsontools.load_json(data)
    #logger.info("json_object="+repr(json_object))
    #logger.info("VOD="+repr(json_object["VOD"]))

    for vod in json_object["VOD"]:
        logger.info("vod="+repr(vod))
        title = vod["nombre_programa"]
        if vod["titulo"]!="":
            title = title + " - " + vod["titulo"]
        if vod["fecha_emision"]!="":
            title = title + " ("+scrapertools.htmlclean(vod["fecha_emision"])+")"
        url = "http://www.rtpa.es/video:"+urllib.quote(vod["nombre_programa"])+"_"+vod["id_generado"]+".html"

        try:
            url_imagen = vod["url_imagen"]
            thumbnail = urllib.quote(url_imagen).replace("//","/").replace("http%3A/","http://")
        except:
            thumbnail = ""

        aired_date = scrapertools.parse_date( vod["fecha_emision"] )
        
        plot = scrapertools.htmlclean(vod["sinopsis"])
        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url,  thumbnail=thumbnail , plot=plot, fanart=thumbnail, server="rtpa", action="play" , show = item.show , viewmode="movie_with_plot", aired_date=aired_date, folder=False) )

    return itemlist

def detalle_episodio(item):

    item.geolocked = "0"
    
    try:
        from servers import rtpa as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def play(item):

    item.server="rtpa";
    itemlist = [item]

    return itemlist

# Test de canal
# Devuelve: Funciona (True/False) y Motivo en caso de que no funcione (String)
def test():
    
    # Carga el menu principal
    items_mainlist = mainlist(Item())

    # Busca el item con la lista de programas
    items_programas = []
    for item_mainlist in items_mainlist:

        if item_mainlist.action=="programas":
            items_programas = programas(item_mainlist)
            break

    if len(items_programas)==0:
        return False,"No hay programas"

    # Carga los episodios
    items_episodios = episodios(items_programas[0])
    if len(items_episodios)==0:
        return False,"No hay episodios en "+items_programas[0].title

    # Lee la URL del vídeo
    item_episodio = detalle_episodio(items_episodios[0])
    if item_episodio.media_url=="":
        return False,"El conector no devuelve enlace para el vídeo "+item_episodio.title

    return True,""
