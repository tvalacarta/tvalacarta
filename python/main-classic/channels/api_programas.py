# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import datetime
import time

from core import api
from core import logger
from core import config
from core import scrapertools
from core.item import Item
from core import suscription

DEBUG = config.get_setting("debug")
CHANNELNAME = "api_programas"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.api_programas mainlist")

    return api.navigation_get_programs_menu(item,viewmode="list",channel=CHANNELNAME)

def videos_get_dates(item):
    logger.info("tvalacarta.channels.api_programas videos_get_dates")

    return api.get_itemlist_from_item(item,viewmode="list",title_field="title_with_count",channel=CHANNELNAME)

def programs_get_genres(item):
    logger.info("tvalacarta.channels.api_programas get_genres")

    return api.get_itemlist_from_item(item,viewmode="list",title_field="title_with_count",channel=CHANNELNAME)

def programs_get_topics(item):
    logger.info("tvalacarta.channels.api_programas get_topics")

    return api.get_itemlist_from_item(item,viewmode="list",title_field="title_with_count",channel=CHANNELNAME)

def programs_get_channels(item):
    logger.info("tvalacarta.channels.api_programas get_channels")

    return api.get_itemlist_from_item(item,viewmode="list",title_field="title_with_count",channel=CHANNELNAME)

def programs_get_countries(item):
    logger.info("tvalacarta.channels.api_programas get_countries")

    return api.get_itemlist_from_item(item,viewmode="list",title_field="title_with_count",channel=CHANNELNAME)

def programs_get_languages(item):
    logger.info("tvalacarta.channels.api_programas get_languages")

    return api.get_itemlist_from_item(item,viewmode="list",title_field="title_with_count",channel=CHANNELNAME)

def programs_get_all(item):
    logger.info("tvalacarta.channels.api_programas programs_get_all")

    return api.get_itemlist_from_item(item,viewmode="series",channel=CHANNELNAME,context="program")

def programs_get_latest(item):
    logger.info("tvalacarta.channels.api_programas programs_get_latest")

    return api.get_itemlist_from_item(item,viewmode="series",channel=CHANNELNAME,context="program")

def search(item,tecleado):
    logger.info("tvalacarta.channels.api_programas search")

    item.url = item.url + urllib.quote_plus(tecleado)

    return api.get_itemlist_from_item(item,viewmode="series",channel=CHANNELNAME,context="program")

def add_to_favorites(item):
    logger.info("tvalacarta.channels.api_programas add_to_favorites item="+repr(item))

    api.add_to_favorites(item.url)
    if config.is_xbmc():
        import xbmc
        xbmc.executebuiltin("XBMC.Container.Refresh()");

def remove_from_favorites(item):
    logger.info("tvalacarta.channels.api_programas remove_from_favorites item="+repr(item))

    api.remove_from_favorites(item.url)
    if config.is_xbmc():
        import xbmc
        xbmc.executebuiltin("XBMC.Container.Refresh()");

def add_to_hidden(item):
    logger.info("tvalacarta.channels.api_programas add_to_hidden item="+repr(item))

    api.add_to_hidden(item.url)
    if config.is_xbmc():
        import xbmc
        xbmc.executebuiltin("XBMC.Container.Refresh()");

def remove_from_hidden(item):
    logger.info("tvalacarta.channels.api_programas remove_from_hidden item="+repr(item))

    api.remove_from_hidden(item.url)
    if config.is_xbmc():
        import xbmc
        xbmc.executebuiltin("XBMC.Container.Refresh()");

def videos_get_by_program(item):
    logger.info("tvalacarta.channels.api_programas videos_get_by_program")

    return api.get_itemlist_from_item(item,viewmode="episodes",channel=CHANNELNAME)

def videos_get_by_date(item):
    logger.info("tvalacarta.channels.api_programas videos_get_by_date")

    itemlist = api.get_itemlist_from_item(item,viewmode="episodes",channel=CHANNELNAME)

    for item in itemlist:
        if item.show_title<>"":
            item.title = item.show_title+" - "+item.title
            item.plot  = "Programa: "+item.show_title+"\n"+"Canal: "+item.channel_title+"\n"+item.plot

    return itemlist

def play(item):
    logger.info("tvalacarta.channels.api_programas play item="+repr(item))

    mark_as_watched(item)

    exec "from channels import "+item.extra+" as channelmodule"

    play_items = channelmodule.play(item)

    valid_url = False
    for play_item in play_items:
        if play_item.server=="directo" and play_item.url.startswith("http"):
            valid_url = True
        if play_item.server<>"directo":
            valid_url = True

    if not valid_url:
        response = api.videos_get_media_url(item.uid)
        play_items = [Item(channel=item.channel, server="directo", url=response["body"])]

    return play_items

def mark_as_watched(item):
    logger.info("tvalacarta.channels.api_programas mark_as_watched item="+repr(item))

def mark_as_unwatched(item):
    logger.info("tvalacarta.channels.api_programas mark_as_unwatched item="+repr(item))

def subscribe_to_program(item):
    logger.info("tvalacarta.channels.api_programas subscribe_to_program item="+repr(item))

    item.action = "videos_get_by_program"
    if not suscription.already_suscribed(item):
        suscription.append_suscription(item)

        if config.is_xbmc():
            import xbmcgui
            xbmcgui.Dialog().ok( "tvalacarta" , "Suscripción a \""+item.title+"\" creada")

            import xbmc
            xbmc.executebuiltin("XBMC.Container.Refresh()");

def unsubscribe_to_program(item):
    logger.info("tvalacarta.channels.api_programas subscribe_to_program item="+repr(item))

    item.action = "videos_get_by_program"
    if suscription.already_suscribed(item):
        suscription.remove_suscription(item)

        if config.is_xbmc():
            import xbmcgui
            xbmcgui.Dialog().ok( "tvalacarta" , "Suscripción a \""+item.title+"\" eliminada" , "Los vídeos que hayas descargado se mantienen" )

            import xbmc
            xbmc.executebuiltin("XBMC.Container.Refresh()");

def download_all_videos(item):
    logger.info("tvalacarta.channels.api_programas download_all_videos item="+repr(item))

    item.action = "videos_get_by_program"

    from platformcode import launcher
    launcher.download_all_episodes(item)
