# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para mitele
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# Por Truenon y Jesus, modificada por Boludiko
# v11
#------------------------------------------------------------

from core import logger
from core import config
from core import scrapertools       
from core.item import Item
from core import jsontools

__channel__ = "mitele"
__category__ = "S,F,A"
__type__ = "generic"
__title__ = "Mi tele"
__language__ = "ES"

DEBUG = config.get_setting("debug")
GLOBAL_HEADERS = [["Accept","text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"],
                  ["Accept-Encoding", "gzip, deflate, sdch"],
                  ["User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36"]]


def isGeneric():
    return True


def mainlist(item):
    logger.info("[mitele.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Directo"   , action="loadlives" , thumbnail = ""))
    itemlist.append( Item(channel=__channel__, title="Series"    , action="series"  , category="series"    , thumbnail = "" , extra="series"))
    itemlist.append( Item(channel=__channel__, title="Programas"    , action="series"  , category="programas"    , thumbnail = "" , extra="programas"))
    itemlist.append( Item(channel=__channel__, title="Informativos"    , action="series"  , category="informativos"    , thumbnail = "" , extra="informativos"))
    itemlist.append( Item(channel=__channel__, title="Deportes"    , action="series"  , category="deportes"    , thumbnail = "" , extra="deportes"))
    itemlist.append( Item(channel=__channel__, title="Gran Hermano"    , action="temporadas"  , category="entretenimiento"    , thumbnail = "" , url="0000000026548"))
    itemlist.append( Item(channel=__channel__, title="Documentales"    , action="documentales"  , category="divulgacion"    , thumbnail = ""))
    itemlist.append( Item(channel=__channel__, title="Música"    , action="series"  , category="musica"    , thumbnail = "" , extra="musica"))
    itemlist.append( Item(channel=__channel__, title="TV Movies"    , action="series"  , category="cine"    , thumbnail = "" , extra="tv-movies"))
    itemlist.append( Item(channel=__channel__, title="Buscar"    , action="search"))

    return itemlist


def search(item, texto):
    logger.info("[mitele.py] search")
    texto = texto.replace(" ", "%20")
    item.url = "http://cdn-search-mediaset.carbyne.ps.ooyala.com/search/v1/full/providers/104951/mini?q={%22query%22:%22"+texto+"%22,%22page_number%22:%221%22,%22page_size%22:%22300%22,%22product_id%22:[%22Free_Web%22,%22Free_Web_Mobile%22,%22Register_Web%22,%22Free_Live_Web%22,%22Register_Live_Web%22]}&include_titles=Series,Season&include_titles=Series,Season&&product_name=test&format=full"
    try:
        return busqueda(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def busqueda(item):
    logger.info("[mitele.py] busqueda")
    
    itemlist = []
    
    data = scrapertools.downloadpage(item.url, headers=GLOBAL_HEADERS)
    data = jsontools.load_json(data)["hits"]["hits"]
    
    for child in data:
        child = child["_source"]

        title = child["localizable_titles"][0]["title_long"]

        try:
            thumbnail = child["images"][0]["url"]
        except:
            try:
                thumbnail = child["thumbnail"]["url"]
            except:
                thumbnail = ""

        try:
            fanart = child["images"][1]["url"]
        except:
            fanart = ""
        try:
            plot = child["localizable_titles"][0]["summary_long"]
        except:
            plot = ""
        if child["videos"]:
            url = "http://player.ooyala.com/player.js?embedCode="+child["videos"][0]["embed_code"]
            itemlist.append( Item(channel=__channel__, action="play", server="mitele", title=title, fulltitle=title, url=url, thumbnail=thumbnail, plot=plot, show=title, category=item.category, fanart=fanart))
        else:
            try:
                url = child["series_id"]
                season = child["season_number"]
                itemlist.append( Item(channel=__channel__, action="capitulos", title=title, fulltitle=title, url=url, thumbnail=thumbnail, plot=plot, show=title, category=item.category, fanart=fanart, extra=season))
            except:
                url = child["external_id"]
                itemlist.append( Item(channel=__channel__, action="temporadas", title=title, fulltitle=title, url=url, thumbnail=thumbnail, plot=plot, show=title, category=item.category, fanart=fanart))
            

    return itemlist


def series(item):
    logger.info("[mitele.py] series")
    itemlist = []
    
    # Extrae los programas
    data = scrapertools.downloadpage("http://cdn-search-mediaset.carbyne.ps.ooyala.com/search/v1/full/providers/104951/mini?q={%22types%22:%22tv_series%22,%22genres%22:[%22_ca_"+item.extra+"%22],%22page_size%22:%221000%22,%22product_id%22:[%22Free_Web%22,%22Free_Web_Mobile%22,%22Register_Web%22,%22Free_Live_Web%22,%22Register_Live_Web%22]}&format=full&size=200&include_titles=Series,Season&&product_name=test&format=full", headers=GLOBAL_HEADERS)
    data = jsontools.load_json(data)["hits"]["hits"]
    
    for child in data:
        child = child["_source"]
        title = child["localizable_titles"][0]["title_long"]
        emision = child["additional_metadata"][2]["value"]
        if emision == "Si":
            title += "[COLOR red] [En emisión][/COLOR]"

        try:
            thumbnail = child["images"][0]["url"]
        except:
            try:
                thumbnail = child["thumbnail"]["url"]
            except:
                thumbnail = ""
        try:
            fanart = child["images"][1]["url"]
        except:
            fanart = ""
        try:
            plot = child["localizable_titles"][0]["summary_long"]
        except:
            plot = ""
        url = child["external_id"]
        itemlist.append( Item(channel=__channel__, action="temporadas" , title=title,  fulltitle=title, url=url, thumbnail=thumbnail, plot=plot, show=title, category=item.category, fanart=fanart))

    itemlist.sort(key=lambda item: item.title)

    return itemlist


def documentales(item):
    logger.info("[mitele.py] documentales")
    itemlist = []

    data = scrapertools.downloadpage("http://cdn-search-mediaset.carbyne.ps.ooyala.com/search/v1/full/providers/104951/mini?q={%22genres%22:%22_ca_documentales%22,%20%22sort%22:{%22field%22:%22title%22,%20%22order%22:%22asc%22},%22lang%22:%22es%22,%22product_id%22:[%22Free_Web%22,%22Free_Web_Mobile%22,%22Register_Web%22,%22Free_Live_Web%22,%22Register_Live_Web%22]}&format=full&include_titles=Series,Season&&product_name=test&format=full", headers=GLOBAL_HEADERS)
    data = jsontools.load_json(data)["hits"]["hits"]
    
    for child in data:
        child = child["_source"]
        title = child["localizable_titles"][0]["title_long"]
        emision = child["additional_metadata"][2]["value"]
        if emision == "Si":
            title += "[COLOR red] [En emisión][/COLOR]"

        try:
            thumbnail = child["images"][0]["url"]
        except:
            try:
                thumbnail = child["thumbnail"]["url"]
            except:
                thumbnail = ""
        try:
            fanart = child["images"][1]["url"]
        except:
            fanart = item.fanart
        try:
            plot = child["localizable_titles"][0]["summary_long"]
        except:
            plot = item.plot
        url = "http://player.ooyala.com/player.js?embedCode="+child["videos"][0]["embed_code"]
        itemlist.append( Item(channel=__channel__, action="play" , title=title,  fulltitle=title, url=url, server="mitele", thumbnail=thumbnail, plot=plot, show=title, category=item.category, fanart=fanart, folder=False))

    itemlist.sort(key=lambda item: item.title)

    return itemlist


def temporadas(item):
    logger.info("[mitele.py] Temporadas")
    itemlist = []

    # Extrae las temporadas
    url = "http://cdn-search-mediaset.carbyne.ps.ooyala.com/search/v1/full/providers/104951/docs/series?series_id=%s&include=Season&size=2000&include_titles=Series,Season&product_name=test&format=full" % item.url
    data = scrapertools.downloadpage(url, headers=GLOBAL_HEADERS)
    data = jsontools.load_json(data)["hits"]["hits"]

    for child in data:
        child = child["_source"]
        title = child["localizable_titles"][0]["title_long"]

        try:
            thumbnail = child["images"][0]["url"]
        except:
            try:
                thumbnail = child["thumbnail"]["url"]
            except:
                thumbnail = ""
        try:
            fanart = child["images"][1]["url"]
        except:
            fanart = item.fanart
        try:
            plot = child["localizable_titles"][0]["summary_long"]
        except:
            plot = item.plot
        url = item.url
        season = child["season_number"]
        itemlist.append( Item(channel=__channel__, action="capitulos" , title=title,  fulltitle=title, url=url, thumbnail=thumbnail, plot=plot, show=title, category=item.category, fanart=fanart, extra=season))
    
    itemlist.sort(key=lambda item: int(item.extra), reverse=True)
    return itemlist


def capitulos(item):
    logger.info("[mitele.py] Capitulos")

    itemlist = []
    # Extrae las temporadas
    url = "http://cdn-search-mediaset.carbyne.ps.ooyala.com/search/v1/full/providers/104951/docs/series?series_id=%s&include=Episode&size=2000&include_titles=Series,Season&product_name=test&format=full" % item.url
    data = scrapertools.downloadpage(url, headers=GLOBAL_HEADERS)
    data = jsontools.load_json(data)["hits"]["hits"]

    for child in data:
        child = child["_source"]
        if item.extra and child["season_number"] == item.extra:
            try:
                title = child["localizable_titles"][0]["title_sort_name"] + " - " + child["localizable_titles"][0]["title_medium"]
            except:
                title = child["localizable_titles"][0]["title_long"]

            try:
                thumbnail = child["images"][0]["url"]
            except:
                try:
                    thumbnail = child["thumbnail"]["url"]
                except:
                    thumbnail = ""
            try:
                fanart = child["images"][1]["url"]
            except:
                fanart = item.fanart
            try:
                plot = child["localizable_titles"][0]["summary_long"]
            except:
                plot = item.plot
            url = "http://player.ooyala.com/player.js?embedCode="+child["videos"][0]["embed_code"]
            orden = int(child["episode_number"])
            itemlist.append( Item(channel=__channel__, action="play" , title=title,  fulltitle=title, url=url, server="mitele", thumbnail=thumbnail, plot=plot, show=title, category=item.category, fanart=fanart, extra=orden, folder=False))
    
    itemlist.sort(key=lambda item: item.extra, reverse=True)
    return itemlist


def loadlives(item):
    logger.info("[mitele.py] loadlives")
    itemlist = []
    
    import time
    tiempo = int(time.time())
    data = scrapertools.downloadpage("http://indalo.mediaset.es/mmc-player/api/mmc/v1/lives.json")
    # Parrilla de programación
    parrilla = jsontools.load_json(data)

    channels = []
    for channel in parrilla:
        programa = channel["name"]
        canal = channel["channel"]
        if canal not in channels:
            channels.append(canal)
            title = canal.capitalize() + " [[COLOR red]" + programa + "[/COLOR]]"
            url = "http://indalo.mediaset.es/mmc-player/api/mmc/v1/%s/live/flash.json" % canal
            data_channel = scrapertools.downloadpage(url)
            embed_code = jsontools.load_json(data_channel)["locations"][0]["yoo"]
            if not embed_code:
                continue
            url = "http://player.ooyala.com/player.js?embedCode="+embed_code
            itemlist.append(item.clone(title=title, action="play", server="mitele", url=url))


    return itemlist


def test():

    # Al entrar sale una lista de programas
    mainlist_items = mainlist(Item())
    programas_items = series(mainlist_items[0])
    if len(programas_items)==0:
        print "La categoria '"+mainlist_item.title+"' no devuelve programas"
        return False

    temporadas_items = temporadas(programas_items[0])
    if len(temporadas_items)==0:
        print "El programa '"+programas_items[0].title+"' no devuelve temporadas"

    episodios_items = capitulos(temporadas_items[0])
    if len(episodios_items)==0:
        print "El programa '"+programas_items[0].title+"' temporada '"+temporadas_items[0].title+"' no devuelve episodios"

    return True
