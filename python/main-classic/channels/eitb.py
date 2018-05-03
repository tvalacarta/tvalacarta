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
MENU_URL = "http://www.eitb.tv/es/menu/getMenu/tv/"
PROGRAMS_URL = "http://www.eitb.tv/es/menu/getMenu/tv/%s"
EPISODES_URL = "http://mam.eitb.eus/mam/REST/ServiceMultiweb/Playlist/MULTIWEBTV/%s"
VIDEO_URL = "http://www.eitb.tv/es/video/dummy/%s/%s/dummy/"
LO_ULTIMO_URL = "http://mam.eitb.eus/mam/REST/ServiceMultiweb/SmartPlaylist/MULTIWEBTV/360/START_DATE/DESC/100/"
LO_MAS_VISTO_URL = "http://mam.eitb.eus/mam/REST/ServiceMultiweb/SmartPlaylist/Most/MULTIWEBTV/360/10/"
SEARCH_URL = "http://www.eitb.tv/es/buscador/result-video/0/"
ETBSAT_URL = "http://etbvnogeo-lh.akamaihd.net/i/ETBEITBEUS_1@300391/master.m3u8"


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


def load_json(data):
    """ callback to transform json string values to utf8 """
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


def get_menu_items(data):
    pattern = r'<node>\s*<title>[^<]+</title>\s*<title_lang>(?P<title>[^<]+)</title_lang>\s*<submenu\s+hash=\"(?P<id>[^\"]+)\"'
    for item in get_parsed_items(data, pattern):
        yield item


def get_program_items(data):
    pattern = r'<node>\s*<title>(?P<title>[^<]+)</title>\s*<submenu\s+hash=\"(?P<id>[^\"]+)\"[^>]+>'
    for item in get_parsed_items(data, pattern):
        yield item


def get_episode_items(data):
    pattern = r'<node>\s*<title>(?P<title>[^<]+)</title>\s*<id>(?P<id>[^<]+)</id>'
    for item in get_parsed_items(data, pattern):
        yield item


def get_parsed_items(data, pattern):
    matches = re.finditer(pattern, data)
    for match in matches:
        yield match.groupdict()


# Core methods
def mainlist(item):
    logger.info("[eitb.py] mainlist")
    data = scrapertools.cachePage(MENU_URL)
    logger.info("[eitb.py] mainlist: %s" % data)
    itemlist = []
    items = get_menu_items(data)
    for item in items:
        itemlist.append(Item(channel=CHANNELNAME, title=item["title"], action="get_programs", folder=True, url=PROGRAMS_URL % item['id']))
    itemlist.append(Item(channel=CHANNELNAME, title="Buscador", action="search", folder=True, url=SEARCH_URL))
    itemlist.append(Item(channel=CHANNELNAME, title="Lo último", action="get_episodes", folder=True, url=LO_ULTIMO_URL))
    itemlist.append(Item(channel=CHANNELNAME, title="Lo más visto", action="get_episodes", folder=True, url=LO_MAS_VISTO_URL))
    itemlist.append(Item(channel=CHANNELNAME, title="ETBSAT", action="play", folder=False, url=ETBSAT_URL))
    return itemlist


def directos(item=None):
    logger.info("tvalacarta.channels.eitb directos")

    itemlist = []

    itemlist.append( Item(channel=CHANNELNAME, title="ETB",        url=ETBSAT_URL, thumbnail="http://media.tvalacarta.info/canales/128x128/eitb.png", category="Autonómicos", action="play", folder=False ) )

    return itemlist

def get_programs(item):
    data = scrapertools.cachePage(item.url)
    logger.info("[eitb.py] get_programs: %s" % data)
    itemlist = []
    program_items = get_program_items(data)
    for item in program_items:
        itemlist.append(Item(channel=CHANNELNAME, title=item["title"], action="get_programs", folder=True, url=PROGRAMS_URL % item['id']))
    episode_items = get_episode_items(data)
    for item in episode_items:
        itemlist.append(Item(channel=CHANNELNAME, title=item["title"], action="get_episodes", folder=True, url=EPISODES_URL % item['id']))
    itemlist.sort(key=lambda item: item.title)
    return itemlist


def get_episodes(item):
    data = scrapertools.cachePage(item.url)
    logger.info("[eitb.py] get_episodes: %s" % data)
    itemlist = []
    episodes = load_json(data)
    if episodes:
        playlist_id = episodes["id"]
        for episode in episodes["web_media"]:
            thumbnail = episode.get("STILL_URL")
            if not thumbnail:
                thumbnail = episode.get("THUMBNAIL_URL", "")
            language = episode.get("IDIOMA", "ES")
            title = safe_unicode(episode.get("NAME_%s" % language, "")).encode("utf-8")
            plot = safe_unicode(episode.get("SHORT_DESC_%s" % language, "")).encode("utf8")
            url = VIDEO_URL % (playlist_id, episode["ID"])
            itemlist.append(Item(channel=CHANNELNAME, title=title, action="play", folder=False, url=url, server=CHANNELNAME, thumbnail=thumbnail, plot=plot))
    return itemlist


def search(item, text):
    logger.info("[eitb.py] search")
    post = urllib.urlencode({"search": text})
    data = scrapertools.cachePage(item.url, post=post)
    logger.info("[eitb.py] search: %s" % data)
    itemlist = []
    episodes = load_json(data)
    for episode in episodes:
        thumbnail = episode.get("THUMBNAIL_URL", "")
        title_start = episode.get("NAME", "")
        title_end = episode.get("TIT_VIDEO")
        if not title_end:
            title_end = episode.get("CAPITULO", "")
        title = safe_unicode("%s (%s)" % (title_start, title_end)).encode("utf-8")
        description = episode.get("DESC_VIDEO")
        if not description:
            description = episode.get("SHORT_DESC", "")
        plot = safe_unicode(description).encode("utf8")
        url = VIDEO_URL % (episode["ID_PLAYLIST"], episode["ID_VIDEO"])
        itemlist.append(Item(channel=CHANNELNAME, title=title, action="play", folder=False, url=url, server=CHANNELNAME, thumbnail=thumbnail, plot=plot))
    return itemlist


def test():
    # Al entrar sale una lista de programas
    menu_items = mainlist(Item())
    if len(menu_items) == 0:
        print("Al entrar a mainlist no sale nada")
        return False

    program_items = get_programs(menu_items[0])
    if len(program_items) == 0:
        print("El programa %s no tiene episodios" % menu_items[0].title)
        return False

    return True
