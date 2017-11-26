# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# tvalacarta 4
# Copyright 2015 tvalacarta@gmail.com
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
# This file is part of tvalacarta 4.
#
# tvalacarta 4 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tvalacarta 4 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tvalacarta 4.  If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------
# XBMC entry point
#------------------------------------------------------------
# Canal para Once TV (México)
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core import jsontools
from core.item import Item
from servers import servertools

__channel__ = "oncetvmex"
__title__ = "oncetvmex"

DEBUG = config.get_setting("debug")
SERVICE_URL = "https://canaloncelive.tv/REST/index.php"

def isGeneric():
    return True

def mainlist(item):
    return categorias(item)

def categorias(item):
    logger.info("tvalacarta.channels.oncetvmex categorias")


    intentos = 0
    while intentos<5:

        try:
            itemlist = []

            # Descarga la página
            categories = scrapertools.cache_page(SERVICE_URL,"module=Web&function=Get_categories")
            categories_json = jsontools.load_json(categories)

            for category_item in categories_json:

                thumbnail = ""
                url = str(category_item["codigo"])
                title = category_item["nombre"]
                plot = ""

                itemlist.append( Item(channel=__channel__, action="programas", title=title, url=url, folder=True))

            break

        except:
            logger.info("tvalacarta.channels.oncetvmex lista vacia, reintentando...")
            intentos = intentos + 1
            import time
            time.sleep(2)

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.oncetvmex programas")    

    intentos = 0
    while intentos<5:

        try:
            itemlist = []

            programs = scrapertools.cache_page(SERVICE_URL,"module=Web&function=Get_programs_in_cat&seccion="+item.url)
            programs_json = jsontools.load_json(programs)

            for program_item in programs_json["programas"]:
                thumbnail = program_item["artwork"]
                url = "https://canaloncelive.tv/index.php?channel="+program_item["xml"]
                title = program_item["name"]
                plot = ""

                itemlist.append( Item(channel=__channel__, action="episodios", title=title, show=title, url=url, thumbnail=thumbnail, fanart=thumbnail, category=item.title, plot=plot, folder=True))

            break

        except:
            logger.info("tvalacarta.channels.oncetvmex lista vacia, reintentando...")
            intentos = intentos + 1
            import time
            time.sleep(2)

    return itemlist

def detalle_programa(item):

    intentos = 0
    while intentos<5:

        try:

            program_id = scrapertools.find_single_match(item.url,"channel=(.*?)$")
            detail = scrapertools.cache_page(SERVICE_URL,"module=Web&function=Get_detail&xml="+program_id)
            detail_json = jsontools.load_json(detail)

            item.plot = detail_json["general"]["descripcion"]

            break

        except:
            logger.info("tvalacarta.channels.oncetvmex lista vacia, reintentando...")
            intentos = intentos + 1
            import time
            time.sleep(2)

    return item

def episodios(item,load_all_pages=True):
    logger.info("tvalacarta.channels.oncetvmex episodios")

    intentos = 0
    while intentos<5:

        try:
            itemlist = []

            program_id = scrapertools.find_single_match(item.url,"channel=(.*?)$")
            data = scrapertools.cache_page(SERVICE_URL,"module=Web&function=Get_detail&xml="+program_id)

            json_data = jsontools.load_json(data)

            for json_item in json_data["programas"]:
                thumbnail = json_item["still"]
                url = json_item["movie"]
                title = json_item["title"]
                plot = json_item["description"]
                logger.info("tvalacarta.channels.oncetvmex episodios title="+title+", url="+url)

                itemlist.append( Item(channel=__channel__, action="play", server="directo", title=title, show=item.show, url=url, thumbnail=thumbnail,  plot=plot, folder=False))

            break

        except:
            logger.info("tvalacarta.channels.oncetvmex lista vacia, reintentando...")
            intentos = intentos + 1
            import time
            time.sleep(2)

    return itemlist

def detalle_episodio(item):

    item.geolocked = "0"    
    item.media_url = item.url

    return item

def play(item):

    item.server="directo";
    itemlist = [item]

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    
    # Mainlist es la lista de programas
    programas_items = mainlist(Item())
    if len(programas_items)==0:
        print "No encuentra los programas"
        return False

    episodios_items = videos(programas_items[0])
    if len(episodios_items)==0:
        print "El programa '"+programas_items[0].title+"' no tiene episodios"
        return False

    return True
