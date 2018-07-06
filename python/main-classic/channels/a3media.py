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
CHANNELID = "5a6b32667ed1a834493ec03b"
MAXLIST = 20

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

    url_sections = "https://api.atresplayer.com/client/v1/row/search?entityType=ATPFormat&sectionCategory=true&mainChannelId=%s&categoryId=%s&sortType=THE_MOST&size=%d&page=0"

    #urlchannels="https://api.atresplayer.com/client/v1/info/categories/"+CHANNELID
    sections = [
		("series",       "5a6a1b22986b281d18a512b8"),
		("programas",    "5a6a1ba0986b281d18a512b9"),
		("noticias",     "5a6a215e986b281d18a512bc"),
		("telenovelas",  "5a6a2313986b281d18a512be"),
		("documentales", "5b067bf3986b28b0a27c2f42"),
		("snacks",       "5b17b5887ed1a87a91038bf5"),
		("deportes",     "5a6a222c986b281d18a512bd"),
		("infantil",     "5a6a24b1986b281d18a512c0")
    ]

    itemlist.append(Item(channel=CHANNELNAME, title="Directos", action="loadlives", folder=True))
    itemlist.append(Item(channel=CHANNELNAME, title="Destacados", action="highlights", folder=True))

    for section in sections:
	urltmp = url_sections % (CHANNELID, section[1], MAXLIST)
        itemlist.append(Item(channel=CHANNELNAME, title=section[0].capitalize(), action="secciones", url=urltmp, folder=True))

    return itemlist


def highlights(item):
    logger.info("tvalacarta.channels.a3media highlights")

    url_highlights = "https://api.atresplayer.com/client/v1/row/%s?size=%d&page=0"

    highlights = [
		("antena3",  "5ac20bcf986b2804f6a9170e"),
		("la Sexta", "5ad6168c986b2866f90617e5"),
		("neox",     "5ae2e631986b2847488e1e8a"),
		("nova",     "5ae2eadf986b2847488e1e94"),
		("mega",     "5ae2ef80986b2847488e1eb0"),
		("flooxer destacados",      "5b16a2557ed1a87a92fe2a1a"),
		("flooxer videos populares", "5b16a2dd7ed1a87a92fe2a1d")
    ]

    itemlist = []
    for hl in highlights:
        urltmp = url_highlights % (hl[1], MAXLIST)
        itemlist.append(Item(channel=CHANNELNAME, title=hl[0].capitalize(), action="episodios", url=urltmp, folder=True))

    return itemlist


def secciones(item):
    logger.info("tvalacarta.channels.a3media secciones")

    itemlist = []
    data = scrapertools.cachePage(item.url)
    #logger.info(data)
    lista = jsontools.load_json(data)
    if lista == None:
	return itemlist

    if lista.has_key('itemRows'):
        for entry in lista['itemRows']:
	    scrapedtitle = entry['title']
	    scrapedurl = entry['link']['href']
	    scrapedthumbnail = entry['image']['pathHorizontal']
	    if entry.has_key('visibility'):
                visibility = entry['visibility']
            else:
                visibility = "FREE"

	    # Solo probado con videos libres. Falta ver qué ocurre con login y paquetes comprados
	    # Si el video no es libre, se lista la entrada, pero no hace nada
            if visibility == "FREE":
                itemlist.append(Item(channel=CHANNELNAME, title=scrapedtitle, action="temporadas", url=scrapedurl, thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, folder=True))
            else:
                itemlist.append(Item(channel=CHANNELNAME, title="["+visibility+"] "+scrapedtitle, action="", url="", thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, folder=False))

    # Paginador
    if lista.has_key('pageInfo'):
        total = lista['pageInfo']['totalPages']
        page = lista['pageInfo']['pageNumber'] + 1
        if total > 1 and page < total:
            nextUrl = item.url[:item.url.find('&page=')] if '&page=' in item.url else item.url
            nextUrl = nextUrl+"&page="+str(page)
            nextTitle = "Página siguiente ("+str(page)+"/"+str(total)+") > > > > "
            itemlist.append(Item(channel=CHANNELNAME, title=nextTitle, action="secciones", url=nextUrl, folder=True))

    return itemlist


def temporadas(item):
    logger.info("tvalacarta.channels.a3media temporadas")

    itemlist = []
    data = scrapertools.cachePage(item.url)
    #logger.info(data)
    lista = jsontools.load_json(data)
    if lista == None:
	return itemlist

    if lista.has_key('rows'):
	itemlist.append(Item(channel=CHANNELNAME, title="Todos", action="episodios", url=lista['rows'][0]['href']+"&size="+str(MAXLIST), folder=True))

    if lista.has_key('seasons'):
        for entry in lista['seasons']:
            scrapedtitle = entry['title']
            scrapedurl = entry['link']['href']
            itemlist.append(Item(channel=CHANNELNAME, title=scrapedtitle, action="menutemporadas", url=scrapedurl, folder=True))

    return itemlist


def episodios(item):
    logger.info("tvalacarta.channels.a3media episodios")

    itemlist = []
    data = scrapertools.cachePage(item.url)
    #logger.info(data)
    lista = jsontools.load_json(data)
    if lista == None:
        return itemlist

    if lista.has_key('itemRows'):
        for entry in lista['itemRows']:
            scrapedtitle = entry['image']['title'] + " | " + entry['title']
            scrapedurl = entry['link']['href']
            scrapedthumbnail = entry['image']['pathHorizontal']
	    if entry.has_key('visibility'):
                visibility = entry['visibility']
            else:
                visibility = "FREE"

            if visibility == "FREE":
                itemlist.append(Item(channel=CHANNELNAME, title=scrapedtitle, action="play", url=scrapedurl, thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, folder=False))
            else:
                itemlist.append(Item(channel=CHANNELNAME, title="["+visibility+"] "+scrapedtitle, action="", url="", thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, folder=False))

    # Paginador
    if lista.has_key('pageInfo'):
	total = lista['pageInfo']['totalPages']
	page = lista['pageInfo']['pageNumber'] + 1
	if total > 1 and page < total:
            nextUrl = item.url[:item.url.find('&page=')] if '&page=' in item.url else item.url
            nextUrl = nextUrl+"&page="+str(page)
            nextTitle = "Página siguiente ("+str(page)+"/"+str(total)+") > > > > "
            itemlist.append(Item(channel=CHANNELNAME, title=nextTitle, action="episodios", url=nextUrl, folder=True))

    return itemlist


def menutemporadas(item):
    logger.info("tvalacarta.channels.a3media temporadas")

    itemlist = []
    data = scrapertools.cachePage(item.url)
    #logger.info(data)
    lista = jsontools.load_json(data)
    if lista == None:
        return itemlist

    if lista.has_key('rows'):
        for entry in lista['rows']:
            scrapedtitle = entry['title']
            scrapedurl = entry['href']
            itemlist.append(Item(channel=CHANNELNAME, title=scrapedtitle, action="episodios", url=scrapedurl+"&size="+str(MAXLIST), folder=True))

    return itemlist


def play(item):
    logger.info("tvalacarta.channels.a3media play")

    # Si es un stream de directo, no lo procesa
    if item.url.startswith("rtmp://") or item.url.startswith("https://livepull1"):
        return [item]
    else:
        data = scrapertools.cachePage(item.url)
        #logger.info(data)
        lista = jsontools.load_json(data)

	if lista == None: return

        if lista.has_key('urlVideo'):
	    data2 = scrapertools.cachePage(lista['urlVideo'])
    	    #logger.info(data2)
	    lista2 = jsontools.load_json(data2)
	    if lista2 == None: return
	    #item.plot=lista2['descripcion']
	    #item.title=lista2['titulo']
	    #item.thumbnail=lista2['imgPoster']
	    item.url=lista2['sources'][0]['src']
	    #item.info_labels={ "Duration" : lista2['duration'] }
            return [item]


def directos(item=None):
    logger.info("tvalacarta.channels.a3media directos")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="La Sexta", url="https://livepull1.secure.footprint.net/geolasextampp/master.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/lasexta.png", category="Nacionales", action="play", folder=False ) )
    itemlist.append( Item(channel=CHANNELNAME, title="Antena 3", url="https://livepull1.secure.footprint.net/geoantena3mpp/master.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/antena3.png", category="Nacionales", action="play", folder=False ) )
    itemlist.append( Item(channel=CHANNELNAME, title="Mega", url="https://livepull1.secure.footprint.net/geomegampp/master.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/mega.png", category="Nacionales", action="play", folder=False ) )
    itemlist.append( Item(channel=CHANNELNAME, title="Neox", url="https://livepull1.secure.footprint.net/geoneoxmpp/master.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/neox.png", category="Nacionales", action="play", folder=False ) )
    itemlist.append( Item(channel=CHANNELNAME, title="Nova", url="https://livepull1.secure.footprint.net/geonovampp/master.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/nova.png", category="Nacionales", action="play", folder=False ) )
    itemlist.append( Item(channel=CHANNELNAME, title="A3Series", url="https://livepull1-i.akamaized.net/geoa3seriesmpp/master.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/a3series.png", category="Nacionales", action="play", folder=False ) )

    return itemlist


# Cargar menú de directos
def loadlives(item):
    logger.info("tvalacarta.channels.a3media play loadlives")

    itemlist = []

    url_ondacero  = "rtmp://ondacerofms35livefs.fplive.net:1935/ondacerofms35live-live/stream-madrid swfVfy=http://www.atresplayer.com/static/swf/swf/oc/AUPlayerBlack.swf pageUrl=http://www.atresplayer.com/directos/radio/onda-cero/ live=true"
    url_europafm  = "rtmp://antena3fms35geobloqueolivefs.fplive.net:1935/antena3fms35geobloqueolive-live/stream-europafm swfVfy=http://www.atresplayer.com/static/swf/swf/efm/AUPlayerBlack.swf pageUrl=http://www.atresplayer.com/directos/radio/europa-fm/ live=true"
    url_melodiafm = "rtmp://ondacerogeofms35livefs.fplive.net:1935/ondacerogeofms35live-live/stream-ondamelodia swfVfy=http://www.atresplayer.com/static/swf/swf/mfm/AUPlayerBlack.swf pageUrl=http://www.atresplayer.com/directos/radio/melodia-fm/ live=true"

    for directo in directos(item):
        itemlist.append(directo)

    itemlist.append( Item(channel=CHANNELNAME, title="Radio: Onda Cero",   action="play", url=url_ondacero,  folder=False) )
    itemlist.append( Item(channel=CHANNELNAME, title="Radio: Europa FM",   action="play", url=url_europafm,  folder=False) )
    itemlist.append( Item(channel=CHANNELNAME, title="Radio: Melodía FM",   action="play", url=url_melodiafm,  folder=False) )

    return itemlist


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

# Test de canal
# Devuelve: Funciona (True/False) y Motivo en caso de que no funcione (String)
def test():
    
    items_mainlist = mainlist(Item())
    series_item = None
    for item in items_mainlist:
        if item.title=="Series":
            series_menu_item = item

    if series_menu_item is None:
        return False,"No hay sección Series en el menu"
            
    # El canal tiene estructura menu -> series -> temporadas -> episodios -> play
    series_items = secciones(series_menu_item)
    if len(series_items)==0:
        return False,"No hay series"

    temporadas_items = temporadas(series_items[0])
    if len(temporadas_items)==0:
        return False,"No hay temporadas"

    episodios_items = episodios(temporadas_items[0])
    if len(episodios_items)==0:
        return False,"No hay episodios"

    play_item = episodios(temporadas_items[0])
    if len(episodios_items)==0:
        return False,"No hay video"

    return True,""
