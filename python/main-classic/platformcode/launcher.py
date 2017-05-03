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
# XBMC Launcher (xbmc / kodi / boxee)
# Taken from pelisalacarta
# ------------------------------------------------------------

import urllib, urllib2
import os,sys

from core import logger
from core import config
from core import downloadtools
from core import scrapertools
from core import api

from core.item import Item
from platformcode import xbmctools

from core.exceptions import UserException
from core.exceptions import InvalidAuthException

import xbmcplugin
import xbmcgui
import sys

def start():
    """ Primera funcion que se ejecuta al entrar en el plugin.
    Dentro de esta funcion deberian ir todas las llamadas a las
    funciones que deseamos que se ejecuten nada mas abrir el plugin.
    """
    logger.info("tvalacarta.platformcode.launcher start")

    # Test if all the required directories are created
    config.verify_directories_created()

    # Check for updates
    api.plugins_get_latest_packages()

def run(item=None):
    logger.info("tvalacarta.platformcode.launcher run")
    
    if item is None:
        # Extract item from sys.argv
        if sys.argv[2]:
            item = Item().fromurl(sys.argv[2])
            params = ""

        # If no item, this is mainlist
        else:
            item = Item(action="selectchannel")
            params = ""

    logger.info(item.tostring())

    # If item has no action, stops here
    if item.action == "":
        logger.info("Item sin accion")
        return

    try:
        # Action for main menu in channelselector
        if item.action=="selectchannel":
            
            import channelselector
            # TODO: Que channelselector devuelva items, procesados por el mismo add_items_to_kodi_directory que el resto
            itemlist = channelselector.mainlist(params, item.url, item.category)

            # Check for updates only on first screen
            if config.get_setting("updatecheck2") == "true":
                logger.info("tvalacarta.platformcode.launcher Check for plugin updates enabled")
                from core import updater
                
                try:
                    version = updater.checkforupdates()

                    if version:
                        import xbmcgui
                        advertencia = xbmcgui.Dialog()
                        advertencia.ok("Versión "+version+" disponible","Ya puedes descargar la nueva versión del plugin\ndesde el listado principal")

                        itemlist.insert(0,Item(title="Descargar version "+version, version=version, channel="updater", action="update", thumbnail=channelselector.get_thumbnail_path() + "Crystal_Clear_action_info.png"))
                except:
                    import xbmcgui
                    advertencia = xbmcgui.Dialog()
                    advertencia.ok("No se puede conectar","No ha sido posible comprobar","si hay actualizaciones")
                    logger.info("channelselector.mainlist Fallo al verificar la actualización")

            else:
                logger.info("tvalacarta.platformcode.launcher Check for plugin updates disabled")

            #xbmctools.add_items_to_kodi_directory(itemlist, item)

        # Action for updating plugin
        elif item.action=="update":

            from core import updater
            updater.update(item)
            if config.get_system_platform()!="xbox":
                import xbmc
                xbmc.executebuiltin( "Container.Refresh" )

        # Action for channel types on channelselector: movies, series, etc.
        elif item.action=="channeltypes":
            import channelselector
            # TODO: Que channelselector devuelva items, procesados por el mismo add_items_to_kodi_directory que el resto
            itemlist = channelselector.channeltypes(params,item.url,item.category)

            #xbmctools.add_items_to_kodi_directory(itemlist, item)

        # Action for channel listing on channelselector
        elif item.action=="listchannels":
            import channelselector
            # TODO: Que channelselector devuelva items, procesados por el mismo add_items_to_kodi_directory que el resto
            itemlist = channelselector.listchannels(params,item.url,item.category)

            #xbmctools.add_items_to_kodi_directory(itemlist, item)

        # Action in certain channel specified in "action" and "channel" parameters
        else:

            # Checks if channel exists
            channel_file = os.path.join( config.get_runtime_path() , 'channels' , item.channel+".py" )
            logger.info("tvalacarta.platformcode.launcher channel_file=%s" % channel_file)

            channel = __import__('channels.%s' % item.channel, fromlist=["channels.%s" % item.channel])
            logger.info("tvalacarta.platformcode.launcher running channel {0} {1}".format(channel.__name__, channel.__file__))


            # Special play action
            if item.action == "play":
                logger.info("tvalacarta.platformcode.launcher play")

                # First checks if channel has a "play" function
                if hasattr(channel, 'play'):
                    logger.info("tvalacarta.platformcode.launcher executing channel 'play' method")
                    itemlist = channel.play(item)

                    if len(itemlist)>0:
                        item = itemlist[0]
                        xbmctools.play_video(item)
                    else:
                        import xbmcgui
                        ventana_error = xbmcgui.Dialog()
                        ok = ventana_error.ok ("plugin", "No hay nada para reproducir")
                else:
                    logger.info("tvalacarta.platformcode.launcher executing core 'play' method")
                    xbmctools.play_video(item)

            elif item.action.startswith("serie_options##"):
                from core import suscription
                import xbmcgui
                dia = xbmcgui.Dialog()
                opciones = []

                suscription_item = Item(channel=item.channel, title=item.show, url=item.url, action=item.action.split("##")[1], extra=item.extra, plot=item.plot, show=item.show, thumbnail=item.thumbnail)

                if not suscription.already_suscribed(suscription_item):
                    opciones.append("Activar descarga automática")
                else:
                    opciones.append("Cancelar descarga automática")

                #opciones.append("Añadir esta serie a favoritos")
                opciones.append("Descargar todos los episodios")
                seleccion = dia.select("Elige una opción", opciones) # "Elige una opción"

                if seleccion==0:
                    if not suscription.already_suscribed(suscription_item):
                        suscription.append_suscription(suscription_item)

                        yes_pressed = xbmcgui.Dialog().yesno( "Descarga automática activada" , "A partir de ahora los nuevos vídeos que se publiquen de este programa se descargarán automáticamente, podrás encontrarlos en la sección 'Descargas'." )

                        if yes_pressed:
                            download_all_episodes(suscription_item,channel)

                    else:
                        suscription.remove_suscription(suscription_item)
                        xbmcgui.Dialog().ok( "Descarga automática cancelada" , "Los vídeos que hayas descargado se mantienen, pero los nuevos ya no se descargarán ellos solos." )

                elif seleccion==1:
                    downloadtools.download_all_episodes(item, channel)

                '''
                elif seleccion==1:
                    from core import favoritos
                    from core import downloadtools
                    import xbmc

                    keyboard = xbmc.Keyboard(downloadtools.limpia_nombre_excepto_1(item.show)+" ["+item.channel+"]")
                    keyboard.doModal()
                    if keyboard.isConfirmed():
                        title = keyboard.getText()
                        favoritos.savebookmark(titulo=title,url=item.url,thumbnail=item.thumbnail,server="",plot=item.plot,fulltitle=title)
                        advertencia = xbmcgui.Dialog()
                        resultado = advertencia.ok(config.get_localized_string(30102) , title , config.get_localized_string(30108)) # 'se ha añadido a favoritos'
                    return
                '''

            elif item.action=="search":
                logger.info("tvalacarta.platformcode.launcher search")

                import xbmc
                keyboard = xbmc.Keyboard("")
                keyboard.doModal()

                itemlist = []
                if (keyboard.isConfirmed()):
                    tecleado = keyboard.getText()
                    #tecleado = tecleado.replace(" ", "+")
                    itemlist = channel.search(item,tecleado)
                    if itemlist is None:
                        itemlist = []

                xbmctools.add_items_to_kodi_directory(itemlist, item)

            else:
                logger.info("tvalacarta.platformcode.launcher executing channel '"+item.action+"' method")
                exec "itemlist = channel."+item.action+"(item)"
                if itemlist is None:
                    itemlist = []

                # Activa el modo biblioteca para todos los canales genéricos, para que se vea el argumento
                handle = sys.argv[1]
                xbmcplugin.setContent(int( handle ),"movies")
                
                # Añade los items a la lista de XBMC
                xbmctools.add_items_to_kodi_directory(itemlist, item)

    except UserException,e:
        import xbmcgui
        xbmcgui.Dialog().ok ("Se ha producido un error", e.value)

    except InvalidAuthException,e:
        import xbmcgui
        xbmcgui.Dialog().ok ("Se ha producido un error", e.value)

        # Invalidate current session
        config.set_setting("account_session","")

        # Goes to main menu
        run(Item(action="selectchannel"))

    except urllib2.URLError,e:
        import traceback
        logger.error(traceback.format_exc())

        import xbmcgui
        ventana_error = xbmcgui.Dialog()
        # Agarra los errores surgidos localmente enviados por las librerias internas
        if hasattr(e, 'reason'):
            logger.info("Razon del error, codigo: %d , Razon: %s" %(e.reason[0],e.reason[1]))
            texto = config.get_localized_string(30050) # "No se puede conectar con el sitio web"
            ok = ventana_error.ok ("plugin", texto)
        # Agarra los errores con codigo de respuesta del servidor externo solicitado     
        elif hasattr(e,'code'):
            logger.info("codigo de error HTTP : %d" %e.code)
            texto = (config.get_localized_string(30051) % e.code) # "El sitio web no funciona correctamente (error http %d)"
            ok = ventana_error.ok ("plugin", texto)    

    except:
        import traceback
        import xbmcgui
        logger.error(traceback.format_exc())
        
        patron = 'File "'+os.path.join(config.get_runtime_path(),"channels","").replace("\\","\\\\")+'([^.]+)\.py"'
        canal = scrapertools.find_single_match(traceback.format_exc(),patron)
        
        if canal:
            xbmcgui.Dialog().ok(
                "Error inesperado en el canal " + canal,
                "Esto suele pasar cuando hay un fallo de conexión, cuando la web del canal "
                "ha cambiado su estructura, o simplemente "
                "porque hay algo mal en tvalacarta.\nPara saber más detalles, consulta el log.")
        else:
            xbmcgui.Dialog().ok(
                "Se ha producido un error",
                "Lamentablemente estas cosas pasan, puedes comprobar el log para averiguar más detalles" )
