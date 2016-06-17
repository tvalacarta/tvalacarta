# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para a3media
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib, urllib2, os

from core import logger
from core import scrapertools
from core.item import Item
from core import jsontools
from core import config

DEBUG = False
CHANNELNAME = "a3media"

import hmac

ANDROID_HEADERS = [ ["User-Agent","Dalvik/1.6.0 (Linux; U; Android 4.3; GT-I9300 Build/JSS15J"] ]

account = (config.get_setting("a3mediaaccount") == "true" )

def isGeneric():
    return True

def openconfig(item):
    if config.get_library_support():
        config.open_settings( )
    return []

def login():
    logger.info("pelisalacarta.channels.a3media login")

    post = "j_username="+config.get_setting('a3mediauser')+"&j_password="+config.get_setting('a3mediapassword')
    data = scrapertools.cachePage("https://servicios.atresplayer.com/j_spring_security_check", post=post)
    if "error" in data:
        logger.info("tvalacarta.channels.a3media Error en el login")
        return False
    else:
        logger.info("tvalacarta.channels.a3media Login correcto")
        return True

def mainlist(item):
    logger.info("tvalacarta.channels.a3media mainlist")
    itemlist = []

    if account:
        log_result = login()

    if not account:
        itemlist.append( Item(channel=CHANNELNAME, title=bbcode_kodi2html("[COLOR yellow]Regístrate y habilita tu cuenta para disfrutar de más contenido[/COLOR]"), action="openconfig", folder=False) )
    elif not log_result:
        itemlist.append( Item(channel=CHANNELNAME, title=bbcode_kodi2html("[COLOR yellow]Error en el login. Comprueba tus credenciales[/COLOR]"), action="openconfig", folder=False) )

    url="http://servicios.atresplayer.com/api/mainMenu"
    data = scrapertools.cachePage(url)
    #logger.info(data)
    lista = jsontools.load_json(data)[0]
    if lista == None: lista =[]

    url2="http://servicios.atresplayer.com/api/categorySections/"


    itemlist.append( Item(channel=CHANNELNAME, title="Directos", action="loadlives", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Destacados", action="episodios", url="http://servicios.atresplayer.com/api/highlights", folder=True) )

    for entry in lista['menuItems']:
        eid = entry['idSection']
        scrapedtitle = entry['menuTitle']
        scrapedurl = url2 + str(eid)
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="secciones" , url=scrapedurl, folder=True, view="programs") )

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
            itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="temporadas" , url=scrapedurl, thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot , extra=str(extra), folder=True, view="videos") )

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
                    itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot , extra=str(extra), folder=True, view="videos") )

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
                            itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra=str(extra2), folder=True, view="videos") )
                    ######## Fin Añadido ######################################

    if n == 1:  #si solo hay una temporada cargar los episodios
        itemlist = episodios(itemlist[0])

    if n == 0 and ids != None:  #si no hay temporadas pueden ser mas secciones
        item.url = "http://servicios.atresplayer.com/api/categorySections/" + str(ids)
        itemlist = secciones(item)

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.a3media episodios")

    data = scrapertools.cachePage(item.url,headers=ANDROID_HEADERS)
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

        if account:
            if tipo == "FREE" or tipo == "REGISTER": #carga los videos que gratuitos y con registro
                # Añade al listado
                itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra = str(extra), folder=False) )
        else:
            if tipo == "FREE": #solo carga los videos que no necesitan registro ni premium
                # Añade al listado
                itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra = str(extra), folder=False) )
    return itemlist

# Cargar menú de directos
def loadlives(item):
    logger.info("tvalacarta.channels.a3media play loadlives")

    itemlist = []

    url_lasexta  = "http://a3live-lh.akamaihd.net/i/lasexta_1@35272/master.m3u8"
    url_antena3  = "http://a3live-lh.akamaihd.net/i/antena3/antena3_1@35248/master.m3u8"
    url_neox  = "http://a3live-lh.akamaihd.net/i/neox/neox_1@35261/master.m3u8"
    url_ondacero  = "rtmp://ondacerofms35livefs.fplive.net:1935/ondacerofms35live-live/stream-madrid swfVfy=http://www.atresplayer.com/static/swf/swf/oc/AUPlayerBlack.swf pageUrl=http://www.atresplayer.com/directos/radio/onda-cero/ live=true"
    url_europafm = "rtmp://antena3fms35geobloqueolivefs.fplive.net:1935/antena3fms35geobloqueolive-live/stream-europafm swfVfy=http://www.atresplayer.com/static/swf/swf/efm/AUPlayerBlack.swf pageUrl=http://www.atresplayer.com/directos/radio/europa-fm/ live=true"
    url_melodiafm = "rtmp://ondacerogeofms35livefs.fplive.net:1935/ondacerogeofms35live-live/stream-ondamelodia swfVfy=http://www.atresplayer.com/static/swf/swf/mfm/AUPlayerBlack.swf pageUrl=http://www.atresplayer.com/directos/radio/melodia-fm/ live=true"

    itemlist.append( Item(channel=CHANNELNAME, title="La Sexta", action="play", url=url_lasexta, folder=False) )
    itemlist.append( Item(channel=CHANNELNAME, title="Antena 3", action="play", url=url_antena3, folder=False) )
    itemlist.append( Item(channel=CHANNELNAME, title="Neox",     action="play", url=url_neox,    folder=False) )
    itemlist.append( Item(channel=CHANNELNAME, title="Radio: Onda Cero",   action="play", url=url_ondacero,  folder=False) )
    itemlist.append( Item(channel=CHANNELNAME, title="Radio: Europa FM",   action="play", url=url_europafm,  folder=False) )
    itemlist.append( Item(channel=CHANNELNAME, title="Radio: Melodía FM",   action="play", url=url_melodiafm,  folder=False) )

    return itemlist


def play(item):
    logger.info("tvalacarta.channels.a3media play")

    itemlist = []

    # Si es un stream de directo, no lo procesa
    if item.url.startswith("rtmp://") or item.url.startswith("http://a3live-lh"):
        itemlist.append(item)
        return itemlist
    else:
        token = d(item.extra, "QWtMLXs414Yo+c#_+Q#K@NN)")
        url = item.url + token

        if account:
            cookies = os.path.join( config.get_data_path(), 'cookies.dat' )
            cookiedatafile = open(cookies,'r')
            cookiedata = cookiedatafile.read()
            cookiedatafile.close();
            jsessionid = scrapertools.find_single_match(cookiedata,"servicios.atresplayer.com.*?JSESSIONID\s+([A-Za-z0-9\+\-]+)")
            ANDROID_HEADERS.append(['Cookie','JSESSIONID='+jsessionid])

        data = scrapertools.cachePage(url,headers=ANDROID_HEADERS)
        logger.info(data)
        lista = jsontools.load_json(data)
        if lista != None: 
            item.url = lista['resultObject']['es']
            logger.info("tvalacarta.channels.a3media item.url="+item.url)
            itemlist.append(item)

        return itemlist


def getApiTime():
    stime = scrapertools.cachePage("http://servicios.atresplayer.com/api/admin/time",headers=ANDROID_HEADERS)
    return long(stime) / 1000L

def d(s, s1):
    l = 30000L + getApiTime()
    s2 = e(s+str(l), s1)
    return "%s|%s|%s" % (s, str(l), s2)

def e(s, s1):
    return hmac.new(s1, s).hexdigest()


def bbcode_kodi2html(text):
    if config.get_platform().startswith("plex") or config.get_platform().startswith("mediaserver"):
        import re
        text = re.sub(r'\[COLOR\s([^\]]+)\]',
                      r'<span style="color: \1">',
                      text)
        text = text.replace('[/COLOR]','</span>')
        text = text.replace('[CR]','<br>')
        text = re.sub(r'\[([^\]]+)\]',
                      r'<\1>',
                      text)
        text = text.replace('"color: white"','"color: auto"')

    return text