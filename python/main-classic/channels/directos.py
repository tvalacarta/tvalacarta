# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Directos
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urllib
import os
import sys

from core import downloadtools
from core import config
from core import logger
from core import samba
from core import api
from core.item import Item

if config.is_xbmc():
    import xbmc

CHANNELNAME = "directos"
DEBUG = True

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.core.directos mainlist")
    itemlist=[]

    channel_list = build_channel_list()

    contador = 0
    for single_channel in channel_list:
    	itemlist.append( Item(channel=CHANNELNAME, action="player_directo", title=single_channel.title, url=single_channel.url, thumbnail=single_channel.thumbnail, category=single_channel.category, source_channel=single_channel.channel, position=contador, folder=False) )
        contador = contador + 1

    return itemlist

def player_directo(item):

    from core import window_player_background
    import plugintools

    window = window_player_background.PlayerWindowBackground("player_background.xml",plugintools.get_runtime_path())
    window.setItemlist(build_channel_list())
    window.setCurrentPosition(item.position)
    window.doModal()
    del window

    return []

def build_channel_list():
    logger.info("tvalacarta.core.directos build_channel_list")

    channel_list = []

    from channels import rtve
    channel_list.extend(rtve.directos())

    from channels import a3media
    channel_list.extend(a3media.directos())

    from channels import mitele
    channel_list.extend(mitele.directos())

    from channels import apunt
    channel_list.extend(apunt.directos())

    from channels import aragontv
    channel_list.extend(aragontv.directos())

    from channels import extremaduratv
    channel_list.extend(extremaduratv.directos())

    from channels import eitb
    channel_list.extend(eitb.directos())

    from channels import tv3
    channel_list.extend(tv3.directos())

    from channels import dwspan
    channel_list.extend(dwspan.directos())

    #from channels import vuittv
    #channel_list.extend(vuittv.directos())

    from channels import adn40
    channel_list.extend(adn40.directos())

    from channels import sieterm
    channel_list.extend(sieterm.directos())

    from channels import canal22
    channel_list.extend(canal22.directos())

    from channels import rtva
    channel_list.extend(rtva.directos())

    from channels import hispantv
    channel_list.extend(hispantv.directos())

    from channels import montecarlo
    channel_list.extend(montecarlo.directos())

    from channels import euronews
    channel_list.extend(euronews.directos())

    channel_list = sorted(channel_list, key=lambda i: i.category if i.category!="Nacionales" else "0")

    return channel_list
