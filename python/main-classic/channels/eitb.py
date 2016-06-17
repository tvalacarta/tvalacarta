# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para EITB
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import logger
from core import scrapertools
from core.item import Item

logger.info("[eitb.py] init")

DEBUG = False
CHANNELNAME = "eitb"


def isGeneric():
    return True


# Some helper methods
def safe_unicode(value):
    """ Generic unicode handling method to parse the titles """
    from types import UnicodeType
    if type(value) is UnicodeType:
        return value
    else:
        try:
            return unicode(value, 'utf-8')
        except:
            return unicode(value, 'iso-8859-1')


def clean_title(title):
    """slugify the titles using the method that EITB uses in
       the website:
       - url: http://www.eitb.tv/resources/js/comun/comun.js
       - method: string2url
    """
    translation_map = {
        'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A', 'Å': 'A', 'Æ': 'E',
        'È': 'E', 'É': 'E', 'Ê': 'E', 'Ë': 'E',
        'Ì': 'I', 'Í': 'I', 'Î': 'I', 'Ï': 'I',
        'Ò': 'O', 'Ó': 'O', 'Ô': 'O', 'Ö': 'O',
        'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'U',
        'Ñ': 'N', '?': '', '¿': '', '!': '',
        '¡': '', ': ': '', '_': '-', 'º': '',
        'ª': 'a', ',': '', '.': '', '(': '',
        ')': '', '@': '', ' ': '-', '&': ''
    }

    val = safe_unicode(title).upper()
    logger.info(val)
    for k, v in translation_map.items():
        val = val.replace(safe_unicode(k), safe_unicode(v))
    logger.info(val)
    return val.lower().encode('utf-8')

def mainlist(item):
    logger.info("[eitb.py] mainlist")
    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Todo", action="programas", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Categorías", action="categorias", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="A-Z", action="alfabetico", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Buscador" , action="search" , folder=True) )

    return itemlist

def search(item,texto):
    logger.info("[eitb.py] search")

    item.url = "?filter=" + texto
    return programas(item)


def alfabetico(item):
    logger.info("[eitb.py] alfabetico")
    itemlist=[]

    letras = "#ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    for letra in letras:
        itemlist.append( Item(channel=CHANNELNAME, title=letra, action="programas", category="alfabetico", url="?inicial="+letra, folder=True) )

    return itemlist

def categorias(item):
    logger.info("[eitb.py] categorias")
    itemlist=[]

    url = 'http://www.eitb.tv/es/'

    # Descarga la página
    data = scrapertools.cachePage(url)
    patron = "<li[^>]*><a href=\"\" onclick\=\"setPlaylistId\('\d+','[^']+','[^']+'\)\;hormigas\.setHormigas\('TV\|Categorías\|([^\|]+)\|[^']+'\)"
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    unique_matches = list(set(matches))

    for categoria in sorted(unique_matches):
        itemlist.append( Item(channel=CHANNELNAME, title='{0} ({1})'.format(categoria, matches.count(categoria)), action="programas", category="categoria", url="?category="+categoria, folder=True) )

    return itemlist

def programas(item):
    logger.info("[eitb.py] programas")
    itemlist=[]

    url = 'http://www.eitb.tv/es/'
    filtro = None

    # Descarga la página
    data = scrapertools.cachePage(url)
    if item.category == "categoria":
        categoria=urlparse.parse_qs(item.url[1:])["category"][0]
        patron = "<li[^>]*><a href=\"\" onclick\=\"setPlaylistId\('(\d+)','([^']+)','([^']+)'\)\;hormigas\.setHormigas\('TV\|Categorías\|" + categoria + "\|[^']+'\)"
    elif item.category == "alfabetico":
        inicial=urlparse.parse_qs(item.url[1:])["inicial"][0]
        if inicial == "#":
            inicial="^A-Za-z"
        else:
            inicial += inicial.lower()
        patron = "<li[^>]*><a href=\"\" onclick\=\"setPlaylistId\('(\d+)','([" + inicial + "][^']+)','([^']+)'\)\;"
    else:
        try:
            filtro=urlparse.parse_qs(item.url[1:])["filter"][0]
        except:
            filtro = False
        patron = "<li[^>]*><a href=\"\" onclick\=\"setPlaylistId\('(\d+)','([^']+)','([^']+)'\)\;"


    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    oldid = -1
    for id,titulo,titulo2 in sorted(set(matches), key=lambda match: (match[1] + match[2]).lower()):
        if id == oldid:
            continue
        if filtro and filtro not in titulo.lower():
            continue
        scrapedtitle = titulo
        if titulo!=titulo2:
            scrapedtitle = scrapedtitle + " - " + titulo2
        scrapedurl = "http://www.eitb.tv/es/get/playlist/"+id
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , folder=True) )
        oldid = id

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.url)
    data_json = load_json(data)

    item.plot = data_json["desc_group"]

    item.thumbnail = scrapertools.find_single_match(data,'<div class="col-xs-8 col-right"[^<]+<img src="([^"]+)"')

    return item

def episodios(item):
    logger.info("[eitb.py] episodios")
    itemlist=[]

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    logger.info(data)
    episodios_json = load_json(data)
    logger.info("[eitb.py] episodios: %s" % data)
    if episodios_json == None : episodios_json = []

    itemlist = []

    for video in episodios_json['web_media']:
        scrapedthumbnail = video['STILL_URL']
        if scrapedthumbnail is None:
            scrapedthumbnail = video['THUMBNAIL_URL']
        if scrapedthumbnail is None:
            scrapedthumbnail = ""
        logger.info("scrapedthumbnail="+scrapedthumbnail)
        scrapedtitle = safe_unicode(video['NAME_ES']).encode("utf-8")
        scrapedplot = safe_unicode(video['SHORT_DESC_ES']).encode("utf8")

        titulo_playlist = episodios_json['name_group'] + ' ' + episodios_json['name_playlist']
        idPlaylist = episodios_json['id']
        titulo_video = scrapedtitle
        titulo_playlist = clean_title(titulo_playlist)
        titulo_video = clean_title(titulo_video)
        id_video = video['ID']
        scrapedurl = 'http://www.eitb.tv/es/video/'+titulo_playlist+"/"+idPlaylist+"/"+id_video+"/"+titulo_video+"/";
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , server="eitb", url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , folder=False) )

    return itemlist

def load_json(data):
    # callback to transform json string values to utf8
    def to_utf8(dct):
        rdct = {}
        for k, v in dct.items() :
            if isinstance(v, (str, unicode)) :
                rdct[k] = v.encode('utf8', 'ignore')
            else :
                rdct[k] = v
        return rdct
    try :
        from lib import simplejson
        json_data = simplejson.loads(data, object_hook=to_utf8)
        return json_data
    except:
        try:
            import json
            json_data = json.loads(data, object_hook=to_utf8)
            return json_data
        except:
            import sys
            for line in sys.exc_info():
                logger.error("%s" % line)

def test():

    # Al entrar sale una lista de programas
    programas_items = mainlist(Item())
    if len(programas_items)==0:
        print "Al entrar a mainlist no sale nada"
        return False

    episodios_items = episodios(programas_items[0])
    if len(episodios_items)==0:
        print "El programa "+programas_items[0].title+" no tiene episodios"
        return False

    return True
