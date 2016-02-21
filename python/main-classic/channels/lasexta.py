# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Canal para la sexta
#------------------------------------------------------------
import urlparse,re

from core import logger
from core import scrapertools
from core.item import Item

logger.info("[sexta.py] init")

DEBUG = True
CHANNELNAME = "lasexta"
MAIN_URL = "http://www.lasexta.com/programas"
def isGeneric():
    return True

def mainlist(item):
    logger.info("[sexta.py] mainlist")
    itemlist=[]
    
    itemlist.append( Item(channel="antena3", title="Series"         , action="series"       , url="http://www.lasexta.com/videos/series.html", folder=True) )
    itemlist.append( Item(channel="antena3", title="Noticias"       , action="series"     , url="http://www.lasexta.com/videos/noticias.html", folder=True) )
    itemlist.append( Item(channel="antena3", title="Programas"      , action="series"    , url="http://www.lasexta.com/videos/programas.html", folder=True) )
    itemlist.append( Item(channel="antena3", title="Xplora"         , action="series"       , url="http://www.lasexta.com/videos/videos-xplora.html", folder=True) )

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    # Todas las opciones tienen que tener algo
    items = mainlist(Item())
    import antena3
    for item in items:
        exec "itemlist=antena3."+item.action+"(item)"
    
        if len(itemlist)==0:
            return False

    # La sección de programas devuelve enlaces
    series_items = antena3.series(items[0])
    for serie_item in series_items:
        episodios_items = antena3.episodios(serie_item)
        if len(episodios_items)>0:
            return True

    return False
