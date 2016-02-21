# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para a3media
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib, urllib2

from core import logger
from core import scrapertools
from core.item import Item
from core import jsontools

DEBUG = False
CHANNELNAME = "a3media"

import hmac


def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.a3media mainlist")

    url="http://servicios.atresplayer.com/api/mainMenu"
    data = scrapertools.cachePage(url)
    #logger.info(data)
    lista = jsontools.load_json(data)[0]
    if lista == None: lista =[]
  
    url2="http://servicios.atresplayer.com/api/categorySections/"
    itemlist = []

    itemlist.append( Item(channel=CHANNELNAME, title="Destacados" , action="episodios" , url="http://servicios.atresplayer.com/api/highlights", folder=True) )

    for entry in lista['menuItems']:
        eid = entry['idSection']
        scrapedtitle = entry['menuTitle']
        scrapedurl = url2 + str(eid)
    
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="secciones" , url=scrapedurl, folder=True) )

    itemlist.append( Item(channel=CHANNELNAME, title="A.....Z" , action="secciones" , url="http://servicios.atresplayer.com/api/sortedCategorySections", folder=True) )


    return itemlist

def secciones(item):
    logger.info("tvalacarta.channels.a3media secciones")

    data = scrapertools.cachePage(item.url)
    #logger.info(data)
    lista = jsontools.load_json(data)
    if lista == None: lista =[]

    itemlist = []

    for entrys in lista:
        try:
            entry = entrys['section']
        except:
            logger.info("tvalacarta.channels.a3media -----------------------")
            logger.info("tvalacarta.channels.a3media error en "+repr(entrys))
            continue
        extra = entry['idSection']
        scrapedtitle = entry['menuTitle']
        scrapedurl = item.url
        if entry.has_key('storyline'): scrapedplot = entry['storyline']
        else: scrapedplot = ""
        scrapedthumbnail = entry['urlImage'].replace('.jpg','03.jpg')
     
        if entry['drm'] == False: ##solo añade las secciones con visualizacion no protegida  
            # Añade al listado
            itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="temporadas" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra=str(extra), folder=True) )

    return itemlist

def temporadas(item):
    logger.info("tvalacarta.channels.a3media temporadas")

    data = scrapertools.cachePage(item.url)
    #logger.info(data)
    lista = jsontools.load_json(data)
    if lista == None: lista =[]

    url2="http://servicios.atresplayer.com/api/episodes/"
    itemlist = []

    scrapedplot=""
    n = 0
    ids = None
    for entrys in lista:
        try:
            entry = entrys['section']
        except:
            logger.info("tvalacarta.channels.a3media -----------------------")
            logger.info("tvalacarta.channels.a3media error en "+repr(entrys))
            continue
        if entry['idSection'] == int(item.extra):
            ids = entry['idSection']
            if entry.has_key('subCategories'):
                for temporada in entry['subCategories']:
                    n += 1
                    extra = temporada['idSection']
                    scrapedtitle = temporada['menuTitle']
                    scrapedurl = url2 + str(extra)
                    if temporada.has_key('storyline'): scrapedplot = temporada['storyline']
                    else: scrapedplot = item.plot
                    scrapedthumbnail = entry['urlImage'].replace('.jpg','03.jpg')

                    # Añade al listado
                    itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra=str(extra), folder=True) )

                    ######## Añadido ##########################################
                    if temporada.has_key('subCategories'):
                        for prueba in temporada['subCategories']:
                            n += 1
                            extra2 = prueba['idSection']
                            scrapedtitle = prueba['menuTitle']
                            scrapedurl = url2 + str(extra2)
                            if prueba.has_key('storyline'): scrapedplot = prueba['storyline']
                            scrapedthumbnail = temporada['urlImage'].replace('.jpg','03.jpg')

                            # Añade al listado
                            itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra=str(extra2), folder=True) )
                    ######## Fin Añadido ######################################

    if n == 1:  #si solo hay una temporada cargar los episodios
        itemlist = episodios(itemlist[0])

    if n == 0 and ids != None:  #si no hay temporadas pueden ser mas secciones
        item.url = "http://servicios.atresplayer.com/api/categorySections/" + str(ids)
        itemlist = secciones(item)

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.a3media episodios")

    data = scrapertools.cachePage(item.url)
    #logger.info(data)
    lista = jsontools.load_json(data)

    if lista == None: lista =[]

    itemlist = []

    if lista.has_key('episodes'):
        episodes = lista['episodes']
    elif lista.has_key('items'):
        episodes = lista['items']
    else:
        episodes = []
    
    for entrys in episodes:
        logger.info("entrys="+repr(entrys))
        if entrys.has_key('episode'):
            entry = entrys['episode']
        elif entrys.has_key('section'):
            continue

        if entry.has_key('type'):
            tipo = entry['type']
        else:
            tipo = "FREE"

        try:
            episode = entry['contentPk']
        except:
            episode = 0

        try :
            scrapedtitle = entry['titleSection']+" "+entry['titleDetail']
        except:
            scrapedtitle = entry['name']
        if tipo == "REGISTER":
            scrapedtitle = scrapedtitle + " (R)"
        elif tipo == "PREMIUM":
            scrapedtitle = scrapedtitle + " (P)"
    
        scrapedurl = "http://servicios.atresplayer.com/api/urlVideo/%s/%s/" % (episode, "android_tablet") 
        extra = episode
        if entry.has_key('storyline'): scrapedplot = entry['storyline']
        else: scrapedplot = item.plot
        scrapedthumbnail = entry['urlImage'].replace('.jpg','03.jpg')
    
        if tipo == "FREE": #solo carga los videos que no necesitan registro ni premium
            # Añade al listado
            itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra = str(extra), folder=False) )

    return itemlist

def play(item):
    logger.info("tvalacarta.channels.a3media play")

    '''
    token = d(item.extra, "puessepavuestramerced")
    url = item.url + token

    headers=[]
    headers.append(["User-Agent","Dalvik/1.6.0 (Linux; U; Android 4.3; GT-I9300 Build/JSS15J"])
    data = scrapertools.cachePage(url,headers=headers)
    logger.info(data)
    lista = jsontools.load_json(data)
    itemlist = []
    if lista != None: 
        item.url = lista['resultObject']['es']
        itemlist.append(item)
    '''
    url = "http://www.pydowntv.com/api/"+item.extra
    logger.info("url="+url)
    itemlist = Item(url=url)

    return itemlist


def getApiTime():
    stime = scrapertools.cachePage("http://servicios.atresplayer.com/api/admin/time")
    return long(stime) / 1000L

def d(s, s1):
    l = 3000L + getApiTime()
    s2 = e(s+str(l), s1)
    return "%s|%s|%s" % (s, str(l), s2)

def e(s, s1):
    return hmac.new(s1, s).hexdigest()
