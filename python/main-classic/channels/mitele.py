# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para mitele
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# Por Truenon y Jesus, modificada por Boludiko
# v11
#------------------------------------------------------------

import urllib
from core import jsontools
from core import logger
from core import scrapertools       
from core.item import Item

CHANNEL = "mitele"


def isGeneric():
    return True


def mainlist(item):
    logger.info("[mitele.py] mainlist")
    return [
        Item(channel=CHANNEL, title="Directos", action="lives",),
        Item(channel=CHANNEL, title="Programas", action="programs", category="programas", extra="programas-tv"),
        Item(channel=CHANNEL, title="Series", action="programs", category="series", extra="series-online"),
        Item(channel=CHANNEL, title="Miniseries", action="programs", category="miniseries", extra="miniseries"),
        Item(channel=CHANNEL, title="Deportes", action="programs", category="deportes", extra="deportes"),
        Item(channel=CHANNEL, title="TV Movies", action="programs", category="cine", extra="tv-movies"),
        Item(channel=CHANNEL, title="Documentales", action="programs", category="divulgacion", extra="documentales"),
        Item(channel=CHANNEL, title="Informativos", action="programs", category="informativos", extra="informativos"),
        Item(channel=CHANNEL, title="Música", action="programs", category="musica", extra="musica"),
        Item(channel=CHANNEL, title="Buscar", action="search")
    ]


def programs(item):
    logger.info("[mitele.py] programs")
    params = {
        'oid': 'bitban',
        'eid': '/automaticIndex/mtweb?url=www.mitele.es/' + item.extra + '/&page=1&id=a-z&size=1000'
    }
    data = scrapertools.downloadpage("https://mab.mediaset.es/1.0.0/get?" + urllib.urlencode(params))
    programs = jsontools.load_json(data)["editorialObjects"]
    return get_programs(programs, item.category)


def get_programs(programs, category):
    logger.info("[mitele.py] get_programs")
    items = []
    for program in programs:
        title = program["title"]
        thumbnail = program["image"]["src"]
        program_type = program["info"]["type"]
        folder = True
        if program_type in ["movie", "episode"]:
            url = "https://www.mitele.es" + program["image"]["href"]
            action = "play"
            folder = False
            if program_type == "episode":
                title = program["image"]["title"]
        else:
            url = "https://mab.mediaset.es/1.0.0/get?oid=bitban&eid=/container/mtweb?url=https://www.mitele.es" + program["image"]["href"]
            action = "seasons"
        items.append(Item(channel=CHANNEL, server=CHANNEL, action=action, title=title, url=url, thumbnail=thumbnail, category=category, folder=folder))
    return items


def seasons(item):
    logger.info("[mitele.py] seasons")
    data = scrapertools.downloadpage(item.url)
    tabs = jsontools.load_json(data)["tabs"]
    items = []
    for tab in tabs:
        if tab["type"] == "navigation" and "contents" in tab:
            for season in tab["contents"]:
                title = season["title"]
                thumbnail = season["images"]["thumbnail"]["src"] if "images" in season and "thumbnail" in season["images"] else ""
                url = "https://mab.mediaset.es/1.0.0/get?oid=bitban&eid=/container/mtweb?url=https://www.mitele.es" + season["link"]["href"]
                season_number = season["info"]["season_number"] if "info" in season else None
                items.append(Item(channel=CHANNEL, action="episodes", title=title, url=url, thumbnail=thumbnail, category=item.category, extra=season_number))
        elif tab["type"] == "automatic-list":
            title = tab["title"]
            params = {
                'oid': 'bitban',
                'eid': '/tabs/mtweb?url=https://www.mitele.es' + tab["link"]["href"] + '&tabId=11796.2'
            }
            url = "https://mab.mediaset.es/1.0.0/get?" + urllib.urlencode(params)
            items.append(Item(channel=CHANNEL, action="episodes", title=title, url=url, category=item.category))
    return items


def episodes(item):
    logger.info("[mitele.py] episodes")
    data = scrapertools.downloadpage(item.url)
    json_data = jsontools.load_json(data)
    tabs = ["tabs"]
    items = []
    if "tabs" in json_data:
        for tab in json_data["tabs"]:
            if tab["type"] in ["navigation", "automatic-list"] and "contents" in tab:
                for season in tab["contents"]:
                    if season["info"]["season_number"] == item.extra:
                        get_episodes(season["children"], item.category, items)
    else:
        get_episodes(json_data["contents"], item.category, items)
    return items


def get_episodes(episodes, category, items):
    logger.info("[mitele.py] get_episodes")
    for episode in episodes:
        title = "%s - %s" % (episode["subtitle"], episode["title"])
        thumbnail = episode["images"]["thumbnail"]["src"]
        url = "https://www.mitele.es" + episode["link"]["href"]
        plot = episode["info"]["synopsis"] if "synopsis" in episode["info"] else ""
        duration = episode["info"]["duration"] if "duration" in episode["info"] else None
        creation_date = episode["info"]["creation_date"] if "creation_date" in episode["info"] else None
        aired_date = scrapertools.parse_date(creation_date) if creation_date else None
        items.append(Item(channel=CHANNEL, server=CHANNEL, action="play", title=title, url=url, thumbnail=thumbnail, 
                            category=category, plot=plot, duration=duration, aired_date=aired_date, folder=False))
    
    

def search(item, texto):
    logger.info("[mitele.py] search")
    try:
        params = {
            'oid': 'bitban',
            'eid': '/search/mtweb?url=www.mitele.es&text=' + texto + '&page=1&size=1000'
        }
        data = scrapertools.downloadpage("https://mab.mediaset.es/1.0.0/get?" + urllib.urlencode(params))
        return get_programs(jsontools.load_json(data)["data"], "search")
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def lives(item=None):
    logger.info("[mitele.py] lives")
    return [
        Item(channel=CHANNEL, action="play", title="Telecinco", url="https://livehlsdai-i.akamaihd.net/hls/live/571640/telecinco/bitrate_4.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/telecinco.png", category="Nacionales", folder=False),
        Item(channel=CHANNEL, action="play", title="Cuatro", url="https://livehlsdai-i.akamaihd.net/hls/live/571643/cuatro/bitrate_4.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/cuatro.png", category="Nacionales", folder=False),
        Item(channel=CHANNEL, action="play", title="Divinity", url="https://mdslivehls-i.akamaihd.net/hls/live/571648/divinity/bitrate_4.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/divinity.png", category="Nacionales", folder=False),
        Item(channel=CHANNEL, action="play", title="Energy", url="https://mdslivehlsb-i.akamaihd.net/hls/live/623617/energy/bitrate_4.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/energy.png", category="Nacionales", folder=False),
        Item(channel=CHANNEL, action="play", title="Be Mad", url="https://mdslivehlsb-i.akamaihd.net/hls/live/623615/bemad/bitrate_4.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/bemad.png", category="Nacionales", folder=False),
        Item(channel=CHANNEL, action="play", title="FDF", url="https://mdslivehls-i.akamaihd.net/hls/live/571650/fdf/bitrate_4.m3u8?xtreamiptv.m3u8", thumbnail="http://media.tvalacarta.info/canales/128x128/fdf.png", category="Nacionales", folder=False)
    ]


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

    return True
