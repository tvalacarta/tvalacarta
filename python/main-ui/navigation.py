# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta 4
# Copyright 2015 tvalacarta@gmail.com
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
#------------------------------------------------------------
# This file is part of pelisalacarta 4.
#
# pelisalacarta 4 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pelisalacarta 4 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pelisalacarta 4.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------

import os
import sys
import urlparse,urllib,urllib2

import xbmc
import xbmcgui
import xbmcaddon

import channelselector
import plugintools
from core.item import Item

def get_next_items( item ):

    plugintools.log("navigation.get_next_items item="+item.tostring())

    try:
        # ----------------------------------------------------------------
        #  Main menu
        # ----------------------------------------------------------------
        if item.channel=="navigation":

            if item.action=="mainlist":
                plugintools.log("navigation.get_next_items Main menu")
                itemlist = channelselector.getmainlist("bannermenu")

        elif item.channel=="channelselector":

            if item.action=="channeltypes":
                plugintools.log("navigation.get_next_items Channel types menu")
                itemlist = channelselector.getchanneltypes("bannermenu")

            if item.action=="program_types":
                plugintools.log("navigation.get_next_items Program types menu")
                itemlist = channelselector.get_program_types("bannermenu")

            elif item.action=="listchannels":
                plugintools.log("navigation.get_next_items Channel list menu")
                itemlist = channelselector.filterchannels(item.category,"bannermenu")

        elif item.channel=="configuracion":
            plugintools.open_settings_dialog()
            return []

        else:

            if item.action=="":
                item.action="mainlist"

            plugintools.log("navigation.get_next_items Channel code ("+item.channel+"."+item.action+")")

            try:
                exec "import channels."+item.channel+" as channel"
            except:
                exec "import core."+item.channel+" as channel"

            from platformcode import xbmctools

            if item.action=="play":
                plugintools.log("navigation.get_next_items play")

                # Si el canal tiene una acción "play" tiene prioridad
                if hasattr(channel, 'play'):
                    plugintools.log("pelisalacarta.platformcode.launcher Channel has its own 'play' method")
                    itemlist = channel.play(item)
                    if len(itemlist)>0:
                        item = itemlist[0]

                        # FIXME: Este error ha que tratarlo de otra manera, al dar a volver sin ver el vídeo falla
                        try:
                            xbmctools.play_video(channel=item.channel, server=item.server, url=item.url, category=item.category, title=item.title, thumbnail=item.thumbnail, plot=item.plot, extra=item.extra, subtitle=item.subtitle, video_password = item.password, fulltitle=item.fulltitle, Serie=item.show)
                        except:
                            pass

                    else:
                        import xbmcgui
                        ventana_error = xbmcgui.Dialog()
                        ok = ventana_error.ok ("plugin", "No hay nada para reproducir")
                else:
                    plugintools.log("pelisalacarta.platformcode.launcher No channel 'play' method, executing core method")

                    # FIXME: Este error ha que tratarlo de otra manera, por al dar a volver sin ver el vídeo falla
                    # Mejor hacer el play desde la ventana
                    try:
                        xbmctools.play_video(channel=item.channel, server=item.server, url=item.url, category=item.category, title=item.title, thumbnail=item.thumbnail, plot=item.plot, extra=item.extra, subtitle=item.subtitle, video_password = item.password, fulltitle=item.fulltitle, Serie=item.show)
                    except:
                        pass


                return []

            elif item.action=="findvideos":
                plugintools.log("navigation.get_next_items findvideos")

                # Si el canal tiene una acción "findvideos" tiene prioridad
                if hasattr(channel, 'findvideos'):
                    plugintools.log("pelisalacarta.platformcode.launcher Channel has its own 'findvideos' method")
                    itemlist = channel.findvideos(item)
                else:
                    itemlist = []

                if len(itemlist)==0:
                    from servers import servertools
                    itemlist = servertools.find_video_items(item)

                if len(itemlist)==0:
                    itemlist = [ Item(title="No se han encontrado vídeos", thumbnail=os.path.join( plugintools.get_runtime_path() , "resources" , "images" , "thumb_error.png" )) ]

            else:

                if item.action=="search":
                    tecleado = plugintools.keyboard_input()
                    if tecleado!="":
                        tecleado = tecleado.replace(" ", "+")
                        itemlist = channel.search(item,tecleado)
                elif item.channel=="novedades" and item.action=="mainlist":
                    itemlist = channel.mainlist(item,"bannermenu")
                elif item.channel=="buscador" and item.action=="mainlist":
                    itemlist = channel.mainlist(item,"bannermenu")
                else:
                    exec "itemlist = channel."+item.action+"(item)"

                for loaded_item in itemlist:

                    if loaded_item.thumbnail=="":
                        if loaded_item.folder:
                            loaded_item.thumbnail = os.path.join( plugintools.get_runtime_path() , "resources" , "images" , "thumb_folder.png" )
                        else:
                            loaded_item.thumbnail = os.path.join( plugintools.get_runtime_path() , "resources" , "images" , "thumb_nofolder.png" )

                if len(itemlist)==0:
                    itemlist = [ Item(title="No hay elementos para mostrar", thumbnail=os.path.join( plugintools.get_runtime_path() , "resources" , "images" , "thumb_error.png" )) ]

    except:
        import traceback
        plugintools.log("navigation.get_next_items "+traceback.format_exc())
        itemlist = [ Item(title="Se ha producido un error", thumbnail=os.path.join( plugintools.get_runtime_path() , "resources" , "images" , "thumb_error.png" )) ]


    return itemlist

def get_window_for_item( item ):
    plugintools.log("navigation.get_window_for_item item.channel="+item.channel+", item.action=="+item.action)

    # El menú principal va con banners + titulo
    if item.channel=="navigation" or (item.channel=="novedades" and item.action=="mainlist") or (item.channel=="buscador" and item.action=="mainlist") or (item.channel=="channelselector" and item.action=="channeltypes") or (item.channel=="channelselector" and item.action=="program_types"):
        import window_channels
        window = window_channels.ChannelWindow("banner.xml",plugintools.get_runtime_path())

    # El listado de canales va con banners sin título
    elif item.channel=="channelselector" and item.action=="listchannels":
        import window_channels
        window = window_channels.ChannelWindow("channels.xml",plugintools.get_runtime_path())

    # El resto va con el aspecto normal
    else:
        import window_menu
        window = window_menu.MenuWindow("content.xml",plugintools.get_runtime_path())

    return window
