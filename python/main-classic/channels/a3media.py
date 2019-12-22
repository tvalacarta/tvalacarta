# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para a3media
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import re

from core import logger
from core import scrapertools
from core.item import Item
from core import jsontools
from core import config

DEBUG = False
CHANNELNAME = "a3media"

account = (config.get_setting("a3mediaaccount") == "true")

def isGeneric():
    return True

def openconfig(item):
    if config.get_library_support():
        config.open_settings( )
    return []

def login():
    logger.info("pelisalacarta.channels.a3media login")
    
    post = "type=credentials&username="+config.get_setting('a3mediauser')+"&password="+config.get_setting('a3mediapassword')
    data = scrapertools.cachePage("https://api.atresplayer.com/login", post=post)
    data = jsontools.load_json(data)
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
        if not log_result:
            itemlist.append(Item(channel=CHANNELNAME, title=bbcode_kodi2html("[COLOR yellow]Error en el login. Comprueba tus credenciales[/COLOR]"), action="openconfig", folder=False))
    else:
        itemlist.append(Item(channel=CHANNELNAME, title=bbcode_kodi2html("[COLOR yellow]Regístrate y habilita tu cuenta para disfrutar de más contenido[/COLOR]"), action="openconfig", folder=False))
    
    itemlist.append(Item(channel=CHANNELNAME, title="Directos", action="loadlives", folder=True))

    url = "https://api.atresplayer.com/client/v1/url?href=%2F"
    data = scrapertools.cachePage(url)
    logger.info(data)
    data = jsontools.load_json(data)
    main_channel_id = data["href"].split("/")[-1]
    
    url = "https://api.atresplayer.com/client/v1/info/categories/%s" % str(main_channel_id)
    data = scrapertools.cachePage(url)
    logger.info(data)
    categories = jsontools.load_json(data)
    for category in categories:
        title = category["title"]
        category_id = category["link"]["href"].split("=")[1]
        url = "https://api.atresplayer.com/client/v1/row/search?entityType=ATPFormat&sectionCategory=true&mainChannelId=%s&categoryId=%s&sortType=AZ&size=100&page=" % (main_channel_id, category_id)
        itemlist.append(Item(channel=CHANNELNAME, title=title, action="programs", url=url, folder=True, view="programs") )

    return itemlist

def programs(item):
    logger.info("tvalacarta.channels.a3media categories")

    data = scrapertools.cachePage(item.url+str(0))
    data = jsontools.load_json(data)
    programs = data["itemRows"]
    total_pages = data["pageInfo"]["totalPages"]
    if total_pages > 1:
        for page in range(1, total_pages):
            data = scrapertools.cachePage(item.url+str(page))
            data = jsontools.load_json(data)
            programs.extend(data["itemRows"])

    itemlist = []
    for program in programs:
        title = program["title"]
        image = program["image"]["pathHorizontal"]
        url = program["link"]["href"]
        itemlist.append(Item(channel=CHANNELNAME, title=title, action="seasons", url=url, thumbnail=image, fanart=image, folder=True, view="videos"))

    return itemlist

def seasons(item):
    logger.info("tvalacarta.channels.a3media seasons")

    data = scrapertools.cachePage(item.url)
    data = jsontools.load_json(data)

    itemlist = []
    format_id = data["id"]
    image = data["image"]["pathHorizontal"]
    plot = data["description"]
    for season in data["seasons"]:
        title = season["title"]
        season_id = season["link"]["href"].split("=")[1]
        url = "https://api.atresplayer.com/client/v1/row/search?entityType=ATPEpisode&formatId=%s&seasonId=%s&sortType=&size=100&page=" % (format_id, season_id)
        itemlist.append(Item(channel=CHANNELNAME, title=title, action="episodes", url=url, thumbnail=image, fanart=image, plot=plot, folder=True, view="videos"))

    return itemlist

def episodes(item):
    logger.info("tvalacarta.channels.a3media episodios")

    data = scrapertools.cachePage(item.url+str(0))
    data = jsontools.load_json(data)
    episodes = data["itemRows"]
    total_pages = data["pageInfo"]["totalPages"]
    if total_pages > 1:
        for page in range(1, total_pages):
            data = scrapertools.cachePage(item.url+str(page))
            data = jsontools.load_json(data)
            episodes.extend(data["itemRows"])

    itemlist = []
    for episode in episodes:
        title = episode["title"]
        image = episode["image"]["pathHorizontal"]        
        plot = "%s\nTipo de contenido: %s" % (episode["image"]["title"], episode["visibility"])
        url = "https://api.atresplayer.com/player/v1/episode/%s" % episode["contentId"]
        itemlist.append(Item(channel=CHANNELNAME, title=title, action="play", url=url, plot=plot, thumbnail=image, folder=False))

    return itemlist

def play(item):
    logger.info("tvalacarta.channels.a3media play")

    itemlist = []
    # If they are not live shows, get the link
    if not item.url.startswith("https://livestartover"):
        data = scrapertools.cachePage(item.url)
        data = jsontools.load_json(data)
        sources = {}
        for source in data["sources"]:
            sources[source["type"]] = source["src"]
        if "application/vnd.apple.mpegurl" in sources.keys():
            item.url = sources["application/vnd.apple.mpegurl"]
        else:
            item.url = sources.values()[0]

    itemlist.append(item)
    
    return itemlist


def loadlives(item=None):
    logger.info("tvalacarta.channels.a3media loadlives")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="La Sexta", url="https://livestartover.atresmedia.com/lasexta/master.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/lasexta.png", category="Nacionales", action="play", folder=False ) )
    itemlist.append( Item(channel=CHANNELNAME, title="Antena 3", url="https://livestartover.atresmedia.com/antena3/master.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/antena3.png", category="Nacionales", action="play", folder=False ) )
    itemlist.append( Item(channel=CHANNELNAME, title="Mega", url="https://livestartover.atresmedia.com/geomega/master.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/mega.png", category="Nacionales", action="play", folder=False ) )
    itemlist.append( Item(channel=CHANNELNAME, title="Neox", url="https://livestartover.atresmedia.com/geoneox/master.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/neox.png", category="Nacionales", action="play", folder=False ) )
    itemlist.append( Item(channel=CHANNELNAME, title="Nova", url="https://livestartover.atresmedia.com/geonova/master.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/nova.png", category="Nacionales", action="play", folder=False ) )
    itemlist.append( Item(channel=CHANNELNAME, title="A3Series", url="https://livestartover.atresmedia.com/geoa3series/master.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/a3series.png", category="Nacionales", action="play", folder=False ) )

    return itemlist


def bbcode_kodi2html(text):
    if config.get_platform().startswith("plex") or config.get_platform().startswith("mediaserver"):
        text = re.sub(r'\[COLOR\s([^\]]+)\]', r'<span style="color: \1">', text)
        text = text.replace('[/COLOR]','</span>')
        text = text.replace('[CR]','<br>')
        text = re.sub(r'\[([^\]]+)\]', r'<\1>', text)
        text = text.replace('"color: white"','"color: auto"')
    return text

# Channel test
def test():
    items_mainlist = mainlist(Item())
    series_item = None
    for item in items_mainlist:
        if item.title == "Series":
            series_menu_item = item

    if series_menu_item is None:
        return False, "There is no Series entry in the menu"

    series_items = programs(series_menu_item)
    if len(series_items) == 0:
        return False, "There are no series"

    temporadas_items = seasons(series_items[0])
    if len(temporadas_items) == 0:
        return False, "There are no seasons"

    episodios_items = episodes(temporadas_items[0])
    if len(episodios_items) == 0:
        return False, "There are no episodes"

    play_item = episodes(temporadas_items[0])
    if len(episodios_items) == 0:
        return False, "There are no videos"

    return True, ""
