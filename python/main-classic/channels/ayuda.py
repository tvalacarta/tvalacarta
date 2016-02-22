# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# tvalacarta - XBMC Plugin
# ayuda - Videos de ayuda y tutoriales para tvalacarta
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#----------------------------------------------------------------------
import re
from core import scrapertools
from core import config
from core import logger
from core.item import Item
from channels import youtube_channel

CHANNELNAME = "ayuda"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.ayuda mainlist")
    itemlist = []

    cuantos = 0
    if config.is_xbmc():
        itemlist.append( Item(channel=CHANNELNAME, action="force_creation_advancedsettings" , title="Crear fichero advancedsettings.xml optimizado"))
        cuantos = cuantos + 1
        
    if cuantos>0:
        itemlist.append( Item(channel=CHANNELNAME, action="tutoriales" , title="Ver guías y tutoriales en vídeo"))
    else:
        itemlist.extend(tutoriales(item))

    return itemlist

def tutoriales(item):
    playlists = youtube_channel.playlists(item,"tvalacarta")

    itemlist = []

    for playlist in playlists:
        if playlist.title=="Tutoriales de tvalacarta":
            itemlist = youtube_channel.videos(playlist)

    return itemlist

def force_creation_advancedsettings(item):

    # Ruta del advancedsettings
    import xbmc,xbmcgui,os
    advancedsettings = xbmc.translatePath("special://userdata/advancedsettings.xml")

    # Copia el advancedsettings.xml desde el directorio resources al userdata
    fichero = open( os.path.join(config.get_runtime_path(),"resources","advancedsettings.xml") )
    texto = fichero.read()
    fichero.close()
    
    fichero = open(advancedsettings,"w")
    fichero.write(texto)
    fichero.close()
                
    dialog2 = xbmcgui.Dialog()
    dialog2.ok("plugin", "Se ha creado un fichero advancedsettings.xml","con la configuración óptima para el streaming.")

    return []
