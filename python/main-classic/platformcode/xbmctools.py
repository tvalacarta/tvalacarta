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
# XBMC Tools (xbmc / kodi / boxee)
# Taken from pelisalacarta
# ------------------------------------------------------------

import urllib, urllib2
import sys
import os

from servers import servertools
from core import config
from core import logger
from core.item import Item
from core import suscription
from channels import descargas

import xbmc
import xbmcgui
import xbmcplugin

DEBUG = False

def play_video(item,desdefavoritos=False,desdedescargados=False,desderrordescargas=False,strmfile=False):
    logger.info('tvalacarta.platformcode.xbmctools add_new_video item='+item.tostring())
    
    if item.url.startswith("http://"):
        item.url = item.url.replace(" ","%20")

    try:
        item.server = item.server.lower()
    except:
        item.server = ""

    if item.server=="":
        item.server="directo"

    view = False
    # Abre el diálogo de selección
    opciones = []
    default_action = config.get_setting("default_action")
    logger.info("default_action="+default_action)

    # Si no es el modo normal, no muestra el diálogo porque cuelga XBMC
    muestra_dialogo = (config.get_setting("player_mode")=="0" and not strmfile)

    # Extrae las URL de los vídeos, y si no puedes verlo te dice el motivo
    video_urls,puedes,motivo = servertools.resolve_video_urls_for_playing(item.server , item.url , item.video_password , item.muestra_dialogo)

    # Si puedes ver el vídeo, presenta las opciones
    if puedes:
        for video_url in video_urls:
            opciones.append(config.get_localized_string(30151) + " " + video_url[0])

        if item.server=="local":
            opciones.append(config.get_localized_string(30164))
        else:
            opcion = config.get_localized_string(30153)
            opciones.append(opcion) # "Descargar"
    
            if item.channel=="favoritos": 
                opciones.append(config.get_localized_string(30154)) # "Quitar de favoritos"
            else:
                opciones.append(config.get_localized_string(30155)) # "Añadir a favoritos"
        
            #if not strmfile:
            #    opciones.append(config.get_localized_string(30161)) # "Añadir a Biblioteca"
        
            if item.channel!="descargas":
                opciones.append(config.get_localized_string(30157)) # "Añadir a lista de descargas"
            else:
                if item.category=="errores":
                    opciones.append(config.get_localized_string(30159)) # "Borrar descarga definitivamente"
                    opciones.append(config.get_localized_string(30160)) # "Pasar de nuevo a lista de descargas"
                else:
                    opciones.append(config.get_localized_string(30156)) # "Quitar de lista de descargas"

            #opciones.append(config.get_localized_string(30158)) # "Enviar a JDownloader"

        if default_action=="3":
            seleccion = len(opciones)-1
    
    # Si no puedes ver el vídeo te informa
    else:
        alert_no_puedes_ver_video(item.server,"",motivo)

        if item.channel=="favoritos": 
            opciones.append(config.get_localized_string(30154)) # "Quitar de favoritos"

        if item.channel=="descargas":
            if item.category=="errores":
                opciones.append(config.get_localized_string(30159)) # "Borrar descarga definitivamente"
            else:
                opciones.append(config.get_localized_string(30156)) # "Quitar de lista de descargas"
        
        if len(opciones)==0:
            return

    # Si la accion por defecto es "Preguntar", pregunta
    if default_action=="0":
        import xbmcgui
        dia = xbmcgui.Dialog()
        seleccion = dia.select(config.get_localized_string(30163), opciones) # "Elige una opción"
        #dia.close()
    elif default_action=="1":
        seleccion = len(video_urls)-1
    elif default_action=="2":
        seleccion = 0
    elif default_action=="3":
        seleccion = seleccion
    else:
        seleccion=0

    logger.info("seleccion=%d" % seleccion)
    logger.info("seleccion=%s" % opciones[seleccion])

    # No ha elegido nada, lo más probable porque haya dado al ESC 
    if seleccion==-1:
        #Para evitar el error "Uno o más elementos fallaron" al cancelar la selección desde fichero strm
        listitem = xbmcgui.ListItem( item.title, iconImage="DefaultVideo.png", thumbnailImage=item.thumbnail)
        import sys
        xbmcplugin.setResolvedUrl(int(sys.argv[ 1 ]),False,listitem)
        return

    if opciones[seleccion]==config.get_localized_string(30158): # "Enviar a JDownloader"
        #d = {"web": url}urllib.urlencode(d)
        from core import scrapertools
        data = scrapertools.cachePage(config.get_setting("jdownloader")+"/action/add/links/grabber0/start1/web="+item.url+ " " +item.thumbnail)
        return

    elif opciones[seleccion]==config.get_localized_string(30164): # Borrar archivo en descargas
        # En "extra" está el nombre del fichero en favoritos
        import os

        os.remove( item.url )

        if os.path.exists(item.url[:-4]+".tbn"):
            os.remove( item.url[:-4]+".tbn" )

        if os.path.exists(item.url[:-4]+".nfo"):
            os.remove( item.url[:-4]+".nfo" )

        xbmc.executebuiltin( "Container.Refresh" )
        return

    # Ha elegido uno de los vídeos
    elif seleccion < len(video_urls):
        mediaurl = video_urls[seleccion][1]
        if len(video_urls[seleccion])>2:
            wait_time = video_urls[seleccion][2]
        else:
            wait_time = 0

        if len(video_urls[seleccion])>3:
            use_download_and_play = (video_urls[seleccion][3]=="download_and_play")
        else:
            use_download_and_play = False

        view = True

    # Descargar
    elif opciones[seleccion]==config.get_localized_string(30153): # "Descargar"
        
        # El vídeo de más calidad es el primero
        mediaurl = video_urls[0][1]
        
        from core import downloadtools
        keyboard = xbmc.Keyboard(item.fulltitle)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            title = keyboard.getText()
            downloadtools.downloadtitle(mediaurl,title)
        return

    elif opciones[seleccion]==config.get_localized_string(30154): #"Quitar de favoritos"
        from channels import favoritos
        # En "extra" está el nombre del fichero en favoritos
        favoritos.deletebookmark(urllib.unquote_plus( item.extra ))

        advertencia = xbmcgui.Dialog()
        resultado = advertencia.ok(config.get_localized_string(30102) , item.title , config.get_localized_string(30105)) # 'Se ha quitado de favoritos'

        xbmc.executebuiltin( "Container.Refresh" )
        return

    elif opciones[seleccion]==config.get_localized_string(30159): #"Borrar descarga definitivamente"
        from channels import descargas
        descargas.delete_error_bookmark(urllib.unquote_plus( item.extra ))

        advertencia = xbmcgui.Dialog()
        resultado = advertencia.ok(config.get_localized_string(30101) , item.title , config.get_localized_string(30106)) # 'Se ha quitado de la lista'
        xbmc.executebuiltin( "Container.Refresh" )
        return

    elif opciones[seleccion]==config.get_localized_string(30160): #"Pasar de nuevo a lista de descargas":
        from channels import descargas
        descargas.mover_descarga_error_a_pendiente(urllib.unquote_plus( item.extra ))

        advertencia = xbmcgui.Dialog()
        resultado = advertencia.ok(config.get_localized_string(30101) , item.title , config.get_localized_string(30107)) # 'Ha pasado de nuevo a la lista de descargas'
        return

    elif opciones[seleccion]==config.get_localized_string(30155): #"Añadir a favoritos":
        from channels import favoritos
        from core import downloadtools

        keyboard = xbmc.Keyboard(item.fulltitle)
        keyboard.doModal()
        if keyboard.isConfirmed():
            title = keyboard.getText()
            favoritos.savebookmark(titulo=title,url=item.url,thumbnail=item.thumbnail,server=item.server,plot=item.plot,fulltitle=item.title)
            advertencia = xbmcgui.Dialog()
            resultado = advertencia.ok(config.get_localized_string(30102) , title , config.get_localized_string(30108)) # 'se ha añadido a favoritos'
        return

    elif opciones[seleccion]==config.get_localized_string(30156): #"Quitar de lista de descargas":
        from channels import descargas
        # La categoría es el nombre del fichero en la lista de descargas
        descargas.deletebookmark((urllib.unquote_plus( item.extra )))

        advertencia = xbmcgui.Dialog()
        resultado = advertencia.ok(config.get_localized_string(30101) , item.title , config.get_localized_string(30106)) # 'Se ha quitado de lista de descargas'

        xbmc.executebuiltin( "Container.Refresh" )
        return

    elif opciones[seleccion]==config.get_localized_string(30157): #"Añadir a lista de descargas":

        from channels import descargas
        from core import downloadtools

        if item.show<>"":
            filename = item.show+" - "+item.title
        elif item.show_title<>"":
            filename = item.show_title+" - "+item.title
        else:
            filename = item.title

        keyboard = xbmc.Keyboard(filename)
        keyboard.doModal()
        if keyboard.isConfirmed():
            filename = keyboard.getText()
            descargas.savebookmark(titulo=filename,url=item.url,thumbnail=item.thumbnail,server=item.server,plot=item.plot,fulltitle=filename)
            advertencia = xbmcgui.Dialog()
            resultado = advertencia.ok(config.get_localized_string(30101) , filename , config.get_localized_string(30109)) # 'se ha añadido a la lista de descargas'
        return

    elif opciones[seleccion]==config.get_localized_string(30161): #"Añadir a Biblioteca":  # Library
        from platformcode.xbmc import library
        titulo = item.fulltitle
        if item.fulltitle=="":
            titulo = item.title
        library.savelibrary(titulo , item.url , item.thumbnail , item.server , item.plot , canal=item.channel , category=item.category , Serie=item.Serie)
        advertencia = xbmcgui.Dialog()
        resultado = advertencia.ok(config.get_localized_string(30101) , item.fulltitle , config.get_localized_string(30135)) # 'se ha añadido a la lista de descargas'
        return

    # Si hay un tiempo de espera (como en megaupload), lo impone ahora
    if wait_time>0:
    
        continuar = handle_wait(wait_time,server,"Cargando vídeo...")
        if not continuar:
            return

    # Obtención datos de la Biblioteca (solo strms que estén en la biblioteca)
    import xbmcgui
    if strmfile:
        xlistitem = getLibraryInfo(mediaurl)
    else:
        try:
            xlistitem = xbmcgui.ListItem( item.title, iconImage="DefaultVideo.png", thumbnailImage=item.thumbnail, path=mediaurl)
        except:
            xlistitem = xbmcgui.ListItem( item.title, iconImage="DefaultVideo.png", thumbnailImage=item.thumbnail)
        xlistitem.setInfo( "video", { "Title": item.title, "Plot" : item.plot , "Studio" : item.channel , "Genre" : item.category } )

    # Lanza el reproductor
    if strmfile: #Si es un fichero strm no hace falta el play
        import sys
        xbmcplugin.setResolvedUrl(int(sys.argv[ 1 ]),True,xlistitem)
        #if subtitle!="" and (opciones[seleccion].startswith("Ver") or opciones[seleccion].startswith("Watch")):
        #    logger.info("tvalacarta.platformcode.xbmctools Con subtitulos")
        #    setSubtitles()
    else:
        if use_download_and_play or config.get_setting("player_mode")=="3":
            import download_and_play

            # El canal exige usar download_and_play, pero el usuario no lo ha elegido -> le quitamos los diálogos
            if use_download_and_play and config.get_setting("player_mode")!="3":
                download_and_play.download_and_play( mediaurl , "download_and_play.tmp" , config.get_setting("downloadpath") , show_dialog=False )
            else:
                download_and_play.download_and_play( mediaurl , "download_and_play.tmp" , config.get_setting("downloadpath") )
            return

        elif config.get_setting("player_mode")=="0":
            # Añadimos el listitem a una lista de reproducción (playlist)
            playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
            playlist.clear()
            playlist.add( mediaurl, xlistitem )

            # Reproduce
            playersettings = config.get_setting('player_type')
            logger.info("tvalacarta.platformcode.xbmctools playersettings="+playersettings)
        
            if config.get_system_platform() == "xbox":
                player_type = xbmc.PLAYER_CORE_AUTO
                if playersettings == "0":
                    player_type = xbmc.PLAYER_CORE_AUTO
                    logger.info("tvalacarta.platformcode.xbmctools PLAYER_CORE_AUTO")
                elif playersettings == "1":
                    player_type = xbmc.PLAYER_CORE_MPLAYER
                    logger.info("tvalacarta.platformcode.xbmctools PLAYER_CORE_MPLAYER")
                elif playersettings == "2":
                    player_type = xbmc.PLAYER_CORE_DVDPLAYER
                    logger.info("tvalacarta.platformcode.xbmctools PLAYER_CORE_DVDPLAYER")
                xbmcPlayer = xbmc.Player( player_type )
            else:
                xbmcPlayer = xbmc.Player()
        
            xbmcPlayer.play(playlist)

        elif config.get_setting("player_mode")=="1":
            #xlistitem.setProperty('IsPlayable', 'true')
            #xlistitem.setProperty('path', mediaurl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path=mediaurl))
        
        elif config.get_setting("player_mode")=="2":
            xbmc.executebuiltin( "PlayMedia("+mediaurl+")" )

    if (config.get_setting("subtitulo") == "true") and view:
        from core import subtitletools
        wait2second()
        subtitletools.set_Subtitle()
        if subtitle!="":
            xbmc.Player().setSubtitles(subtitle)

def handle_wait(time_to_wait,title,text):
    logger.info ("[xbmctools.py] handle_wait(time_to_wait=%d)" % time_to_wait)
    import xbmc,xbmcgui
    espera = xbmcgui.DialogProgress()
    ret = espera.create(' '+title)

    secs=0
    percent=0
    increment = int(100 / time_to_wait)

    cancelled = False
    while secs < time_to_wait:
        secs = secs + 1
        percent = increment*secs
        secs_left = str((time_to_wait - secs))
        remaining_display = ' Espera '+secs_left+' segundos para que comience el vídeo...'
        espera.update(percent,' '+text,remaining_display)
        xbmc.sleep(1000)
        if (espera.iscanceled()):
             cancelled = True
             break

    if cancelled == True:     
         logger.info ('Espera cancelada')
         return False
    else:
         logger.info ('Espera finalizada')
         return True

# Adds all the items to the Kodi directory
def add_items_to_kodi_directory(itemlist,parent_item):
    logger.info("tvalacarta.platformcode.xbmctools add_items_to_kodi_directory")

    pluginhandle = int( sys.argv[ 1 ] )

    # Checks if channel provides context menu for items
    exec "import channels."+parent_item.channel+" as channelmodule"
    channel_provides_context_menu = hasattr(channelmodule, 'get_context_menu_for_item')

    for item in itemlist:

        # If video has no fanart, here is assigned a new one
        if item.fanart=="":
            channel_fanart = os.path.join( config.get_runtime_path(), 'resources', 'images', 'fanart', item.channel+'.jpg')

            if os.path.exists(channel_fanart):
                item.fanart = channel_fanart
            else:
                item.fanart = os.path.join(config.get_runtime_path(),"fanart.jpg")

        # Add item to kodi directory
        add_item_to_kodi_directory(item,itemlist,channel_provides_context_menu)

    # Closes the XBMC directory
    xbmcplugin.setPluginCategory( handle=pluginhandle, category=parent_item.category )
    xbmcplugin.addSortMethod( handle=pluginhandle, sortMethod=xbmcplugin.SORT_METHOD_NONE )

    # Forces the view mode
    if config.get_setting("forceview")=="true":

        import plugintools

        if parent_item.view=="list":
            plugintools.set_view( plugintools.LIST )
        elif parent_item.view=="programs":
            plugintools.set_view( plugintools.TV_SHOWS )
        elif parent_item.view=="channels" or parent_item.view=="thumbnails":

            if config.get_platform()=="kodi-krypton":
                plugintools.set_view( plugintools.TV_SHOWS )
            else:
                plugintools.set_view( plugintools.THUMBNAIL )
        elif parent_item.view=="videos":
            plugintools.set_view( plugintools.EPISODES )

    xbmcplugin.endOfDirectory( handle=pluginhandle, succeeded=True )

def add_item_to_kodi_directory( item , itemlist , channel_provides_context_menu = False ):
    logger.info('tvalacarta.platformcode.xbmctools add_item_to_kodi_directory item='+item.tostring())

    pluginhandle = int( sys.argv[ 1 ] )

    if item.fulltitle=="":
        item.fulltitle = item.title

    logger.info('tvalacarta.platformcode.xbmctools add_item_to_kodi_directory item.is_favorite_show='+item.is_favorite_show)

    # La marca de visto tiene prioridad sobre la de favorito
    if item.watched=="true":
        marca_visto = "(visto) "
        display_title = "[COLOR FF666666]"+marca_visto+item.title+"[/COLOR]"
    
    elif item.is_favorite=="true" or item.is_favorite_show=="true":
        display_title = "[COLOR yellow]"+item.title+"[/COLOR]"
    
    else:
        display_title = item.title

    # Item is a folder
    if item.folder:

        kodi_item = xbmcgui.ListItem( display_title, iconImage="DefaultFolder.png", thumbnailImage=item.thumbnail )
        kodi_item.setInfo( "video", { "Title" : display_title, "Plot" : item.plot, "Studio" : item.channel, "Year" : item.date[0:4] } )

    # Item is playable
    else:

        kodi_item = xbmcgui.ListItem( display_title, iconImage="DefaultVideo.png", thumbnailImage=item.thumbnail )
        kodi_item.setInfo( "video", { "Title" : display_title, "Plot" : item.plot, "Duration" : item.duration, "Studio" : item.canal , "Size": item.size, "Premiered": item.aired_date} )

        # Esta opcion es para poder utilizar el xbmcplugin.setResolvedUrl()
        if config.get_setting("player_mode")=="1": 
            kodi_item.setProperty('IsPlayable', 'true')

    # Add the fanart 
    if item.fanart!="":
        kodi_item.setProperty('fanart_image',item.fanart) 
        #xbmcplugin.setPluginFanart(pluginhandle, item.fanart)

    # This only aplies to unicode strings. The rest stay as they are.
    try:
        item.title = item.title.encode("utf-8")
        item.plot  = item.plot.encode("utf-8")
    except:
        pass

    itemurl = '%s?%s' % ( sys.argv[ 0 ] , item.tourl())

    if config.get_platform()=="boxee":
        success = xbmcplugin.addDirectoryItem( handle=pluginhandle, url=itemurl , listitem=kodi_item, isFolder=item.folder)

    else:
        context_commands = get_context_menu_for_item(item,channel_provides_context_menu)
        
        if len(context_commands)>0:
            kodi_item.addContextMenuItems(context_commands, replaceItems=True)
    
        success = xbmcplugin.addDirectoryItem( handle=pluginhandle, url=itemurl , listitem=kodi_item, isFolder=item.folder, totalItems=len(itemlist) )

    return success

def get_context_menu_for_item( item , channel_provides_context_menu=False ):
    #logger.info("tvalacarta.platformcode.xbmctools get_context_menu_for_item")

    context_menu = []

    # Defines the standard context menus
    # TODO: Reproducir desde aquí
    # TODO: Quitar menu contextual XBMC

    # Then appens the context menus defined by channel
    if channel_provides_context_menu:
        exec "import channels."+item.channel+" as channelmodule"

        itemlist = channelmodule.get_context_menu_for_item(item)

        for item in itemlist:

            itemurl = '%s?%s' % ( sys.argv[ 0 ] , item.tourl())
            command = "XBMC.RunPlugin("+itemurl+")"
            context_menu.append( (item.command_title,command) )

    return context_menu

# TODO: Pasar esto a custom player
def wait2second():
    logger.info("tvalacarta.platformcode.xbmctools wait2second")

    import time
    contador = 0
    while xbmc.Player().isPlayingVideo()==False:
        logger.info("tvalacarta.platformcode.xbmctools setSubtitles: Waiting 2 seconds for video to start before setting subtitles")
        time.sleep(2)
        contador = contador + 1
        
        if contador>10:
            break

# TODO: Pasar esto a custom player
def setSubtitles():
    logger.info("tvalacarta.platformcode.xbmctools setSubtitles")
    import time
    contador = 0
    while xbmc.Player().isPlayingVideo()==False:
        logger.info("tvalacarta.platformcode.xbmctools setSubtitles: Waiting 2 seconds for video to start before setting subtitles")
        time.sleep(2)
        contador = contador + 1
        
        if contador>10:
            break

    subtitlefile = os.path.join( config.get_data_path(), 'subtitulo.srt' )
    logger.info("tvalacarta.platformcode.xbmctools setting subtitle file %s" % subtitlefile)
    xbmc.Player().setSubtitles(subtitlefile)

def alert_no_puedes_ver_video(server,url,motivo):
    import xbmcgui

    if server!="":
        advertencia = xbmcgui.Dialog()
        if "<br/>" in motivo:
            resultado = advertencia.ok( "No puedes ver ese vídeo porque...",motivo.split("<br/>")[0],motivo.split("<br/>")[1],url)
        else:
            resultado = advertencia.ok( "No puedes ver ese vídeo porque...",motivo,url)
    else:
        resultado = advertencia.ok( "No puedes ver ese vídeo porque...","El servidor donde está alojado no está","soportado en tvalacarta todavía",url)
