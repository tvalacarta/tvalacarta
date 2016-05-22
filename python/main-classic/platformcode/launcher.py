# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta
# XBMC Launcher (xbmc / xbmc-dharma / boxee)
# http://blog.tvalacarta.info/plugin-xbmc/
#------------------------------------------------------------

import urllib, urllib2
import os,sys

from core import logger
from core import config

def run():
    logger.info("[launcher.py] run")
    
    # Test if all the required directories are created
    config.verify_directories_created()
    
    # Extract parameters from sys.argv
    params, channel_name, title, channel_title, show_title, fulltitle, url, thumbnail, plot, uid, action, server, extra, subtitle, category, show, password = extract_parameters()
    logger.info("[launcher.py] channel_name=%s, title=%s, fulltitle=%s, url=%s, thumbnail=%s, plot=%s, action=%s, server=%s, extra=%s, subtitle=%s, category=%s, show=%s, password=%s" % (channel_name, title, fulltitle, url, thumbnail, plot, action, server, extra, subtitle, category, show, password))

    if action=="":
        return

    try:
        # Accion por defecto - elegir canal
        if ( action=="selectchannel" ):
            # Borra el fichero de las cookies para evitar problemas con MV
            #ficherocookies = os.path.join( config.get_data_path(), 'cookies.lwp' )
            #if os.path.exists(ficherocookies):
            #    os.remove(ficherocookies)
            
            if config.get_setting("updatechannels")=="true":
                try:
                    from core import updater
                    actualizado = updater.updatechannel("channelselector")

                    if actualizado:
                        import xbmcgui
                        advertencia = xbmcgui.Dialog()
                        advertencia.ok("tvalacarta",config.get_localized_string(30064))
                except:
                    pass

            import channelselector as plugin
            plugin.mainlist(params, url, category)

        # Actualizar version
        elif ( action=="update" ):
            try:
                from core import updater
                updater.update(params)
            except ImportError:
                logger.info("[launcher.py] Actualizacion automática desactivada")

            #import channelselector as plugin
            #plugin.listchannels(params, url, category)
            if config.get_system_platform()!="xbox":
                import xbmc
                xbmc.executebuiltin( "Container.Refresh" )

        elif (action=="channeltypes"):
            import channelselector as plugin
            plugin.channeltypes(params,url,category)

        elif (action=="listchannels"):
            import channelselector as plugin
            plugin.listchannels(params,url,category)

        # El resto de acciones vienen en el parámetro "action", y el canal en el parámetro "channel"
        else:
            if action=="mainlist" and config.get_setting("updatechannels")=="true":
                try:
                    from core import updater
                    actualizado = updater.updatechannel(channel_name)

                    if actualizado:
                        import xbmcgui
                        advertencia = xbmcgui.Dialog()
                        advertencia.ok("plugin",channel_name,config.get_localized_string(30063))
                except:
                    pass

            # La acción puede estar en el core, o ser un canal regular. El buscador es un canal especial que está en pelisalacarta
            regular_channel_path = os.path.join( config.get_runtime_path() , 'channels' , channel_name+".py" )
            core_channel_path = os.path.join( config.get_runtime_path(), 'core' , channel_name+".py" )
            logger.info("[launcher.py] regular_channel_path=%s" % regular_channel_path)
            logger.info("[launcher.py] core_channel_path=%s" % core_channel_path)

            if channel_name=="buscador":
                import pelisalacarta.buscador as channel
            elif os.path.exists( regular_channel_path ):
                exec "import channels."+channel_name+" as channel"
            elif os.path.exists( core_channel_path ):
                exec "from core import "+channel_name+" as channel"

            logger.info("[launcher.py] running channel %s %s" % (channel.__name__ , channel.__file__))

            generico = False
            # Esto lo he puesto asi porque el buscador puede ser generico o normal, esto estará asi hasta que todos los canales sean genericos 
            if category == "Buscador_Generico":
                generico = True
            else:
                try:
                    generico = channel.isGeneric()
                except:
                    generico = False

            if not generico:
                logger.info("[launcher.py] xbmc native channel")
                if (action=="strm"):
                    from platformcode import xbmctools
                    xbmctools.playstrm(params, url, category)
                else:
                    exec "channel."+action+"(params, url, category)"
            else:            
                logger.info("[launcher.py] multiplatform channel")
                from core.item import Item
                item = Item(channel=channel_name, title=title , channel_title=channel_title , show_title=show_title , fulltitle=fulltitle, url=url, thumbnail=thumbnail , plot=plot , uid=uid, server=server, category=category, extra=extra, subtitle=subtitle, show=show, password=password)
                
                '''
                if item.subtitle!="":
                    logger.info("[launcher.py] Downloading subtitle file "+item.subtitle)
                    from core import downloadtools
                    
                    ficherosubtitulo = os.path.join( config.get_data_path() , "subtitulo.srt" )
                    if os.path.exists(ficherosubtitulo):
                        os.remove(ficherosubtitulo)

                    downloadtools.downloadfile(item.subtitle, ficherosubtitulo )
                    config.set_setting("subtitulo","true")
                else:
                    logger.info("[launcher.py] No subtitle")
                '''
                from platformcode import xbmctools

                if action=="play":
                    logger.info("[launcher.py] play")
                    # Si el canal tiene una acción "play" tiene prioridad
                    if hasattr(channel, 'play'):
                        logger.info("[launcher.py] executing channel 'play' method")
                        itemlist = channel.play(item)
                        if len(itemlist)>0:
                            item = itemlist[0]
                            xbmctools.play_video(channel=channel_name, server=item.server, url=item.url, category=item.category, title=item.title, thumbnail=item.thumbnail, plot=item.plot, extra=item.extra, subtitle=item.subtitle, video_password = item.password, fulltitle=item.fulltitle)
                        else:
                            import xbmcgui
                            ventana_error = xbmcgui.Dialog()
                            ok = ventana_error.ok ("plugin", "No hay nada para reproducir")
                    else:
                        logger.info("[launcher.py] no channel 'play' method, executing core method")
                        xbmctools.play_video(channel=channel_name, server=item.server, url=item.url, category=item.category, title=item.title, thumbnail=item.thumbnail, plot=item.plot, extra=item.extra, subtitle=item.subtitle, video_password = item.password, fulltitle=item.fulltitle)

                elif action=="strm_detail" or action=="play_from_library":
                    logger.info("[launcher.py] play_from_library")

                    fulltitle = item.show + " " + item.title
                    elegido = Item(url="")                    

                    logger.info("item.server=#"+item.server+"#")
                    # Ejecuta find_videos, del canal o común
                    try:
                        itemlist = channel.findvideos(item)
                    except:
                        from servers import servertools
                        itemlist = servertools.find_video_items(item)

                    if len(itemlist)>0:
                        #for item2 in itemlist:
                        #    logger.info(item2.title+" "+item2.subtitle)
    
                        # El usuario elige el mirror
                        opciones = []
                        for item in itemlist:
                            opciones.append(item.title)
                    
                        import xbmcgui
                        dia = xbmcgui.Dialog()
                        seleccion = dia.select(config.get_localized_string(30163), opciones)
                        elegido = itemlist[seleccion]
    
                        if seleccion==-1:
                            return
                    else:
                        elegido = item
                
                    # Ejecuta el método play del canal, si lo hay
                    try:
                        itemlist = channel.play(elegido)
                        item = itemlist[0]
                    except:
                        item = elegido
                    logger.info("Elegido %s (sub %s)" % (item.title,item.subtitle))
                    
                    from platformcode import xbmctools
                    logger.info("subtitle="+item.subtitle)
                    xbmctools.play_video(strmfile=True, channel=item.channel, server=item.server, url=item.url, category=item.category, title=item.title, thumbnail=item.thumbnail, plot=item.plot, extra=item.extra, subtitle=item.subtitle, video_password = item.password, fulltitle=fulltitle)

                elif action=="add_pelicula_to_library":
                    logger.info("[launcher.py] add_pelicula_to_library")
                    from platformcode import library
                    # Obtiene el listado desde el que se llamó
                    library.savelibrary( titulo=item.fulltitle , url=item.url , thumbnail=item.thumbnail , server=item.server , plot=item.plot , canal=item.channel , category="Cine" , Serie=item.show.strip() , verbose=False, accion="play_from_library", pedirnombre=False, subtitle=item.subtitle )

                elif action=="add_serie_to_library":
                    logger.info("[launcher.py] add_serie_to_library")
                    from platformcode import library
                    import xbmcgui
                
                    # Obtiene el listado desde el que se llamó
                    action = item.extra
                    exec "itemlist = channel."+action+"(item)"

                    # Progreso
                    pDialog = xbmcgui.DialogProgress()
                    ret = pDialog.create('pelisalacarta', 'Añadiendo episodios...')
                    pDialog.update(0, 'Añadiendo episodio...')
                    totalepisodes = len(itemlist)
                    logger.info ("[launcher.py] Total Episodios:"+str(totalepisodes))
                    i = 0
                    errores = 0
                    nuevos = 0
                    for item in itemlist:
                        i = i + 1
                        pDialog.update(i*100/totalepisodes, 'Añadiendo episodio...',item.title)
                        if (pDialog.iscanceled()):
                            return
                
                        try:
                            #(titulo="",url="",thumbnail="",server="",plot="",canal="",category="Cine",Serie="",verbose=True,accion="strm",pedirnombre=True):
                            # Añade todos menos el último (el que dice "Añadir esta serie...")
                            if i<len(itemlist):
                                nuevos = nuevos + library.savelibrary( titulo=item.title , url=item.url , thumbnail=item.thumbnail , server=item.server , plot=item.plot , canal=item.channel , category="Series" , Serie=item.show.strip() , verbose=False, accion="play_from_library", pedirnombre=False, subtitle=item.subtitle )
                        except IOError:
                            import sys
                            for line in sys.exc_info():
                                logger.error( "%s" % line )
                            logger.info("[launcher.py]Error al grabar el archivo "+item.title)
                            errores = errores + 1
                        
                    pDialog.close()
                    
                    # Actualizacion de la biblioteca
                    itemlist=[]
                    if errores > 0:
                        itemlist.append(Item(title="ERROR, la serie NO se ha añadido a la biblioteca o lo ha hecho incompleta"))
                        logger.info ("[launcher.py] No se pudo añadir "+str(errores)+" episodios")
                    else:
                        itemlist.append(Item(title="La serie se ha añadido a la biblioteca"))
                        logger.info ("[launcher.py] Ningún error al añadir "+str(errores)+" episodios")
                    
                    # FIXME:jesus Comentado porque no funciona bien en todas las versiones de XBMC
                    #library.update(totalepisodes,errores,nuevos)
                    xbmctools.renderItems(itemlist, params, url, category)
                    
                    #Lista con series para actualizar
                    nombre_fichero_config_canal = os.path.join( config.get_data_path() , "series.xml" )
                    logger.info("nombre_fichero_config_canal="+nombre_fichero_config_canal)
                    if not os.path.exists(nombre_fichero_config_canal):
                        f = open( nombre_fichero_config_canal , "w" )
                    else:
                        f = open( nombre_fichero_config_canal , "r" )
                        contenido = f.read()
                        f.close()
                        f = open( nombre_fichero_config_canal , "w" )
                        f.write(contenido)
                    f.write(item.show+","+item.url+","+item.channel+"\n")
                    f.close();

                elif action.startswith("serie_options##"):
                    from core import suscription
                    import xbmcgui
                    dia = xbmcgui.Dialog()
                    opciones = []

                    suscription_item = Item(channel=item.channel, title=item.show, url=item.url, action=action.split("##")[1], extra=item.extra, plot=item.plot, show=item.show, thumbnail=item.thumbnail)

                    if not suscription.already_suscribed(suscription_item):
                        opciones.append("Suscribirme a esta serie")
                    else:
                        opciones.append("Quitar suscripción a esta serie")

                    #opciones.append("Añadir esta serie a favoritos")
                    opciones.append("Descargar todos los episodios")
                    seleccion = dia.select("Elige una opción", opciones) # "Elige una opción"

                    if seleccion==0:
                        if not suscription.already_suscribed(suscription_item):
                            suscription.append_suscription(suscription_item)

                            yes_pressed = xbmcgui.Dialog().yesno( "tvalacarta" , "Suscripción a \""+suscription_item.title+"\" creada" , "¿Quieres descargar los vídeos existentes ahora?" )

                            if yes_pressed:
                                download_all_episodes(suscription_item,channel)

                        else:
                            suscription.remove_suscription(suscription_item)
                            xbmcgui.Dialog().ok( "tvalacarta" , "Suscripción a \""+suscription_item.title+"\" eliminada" , "Los vídeos que hayas descargado se mantienen" )

                    elif seleccion==1:
                        download_all_episodes(suscription_item,channel)

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

                elif action=="search":
                    logger.info("[launcher.py] search")
                    import xbmc
                    keyboard = xbmc.Keyboard("")
                    keyboard.doModal()
                    if (keyboard.isConfirmed()):
                        tecleado = keyboard.getText()
                        #tecleado = tecleado.replace(" ", "+")
                        itemlist = channel.search(item,tecleado)
                    else:
                        itemlist = []
                    xbmctools.renderItems(itemlist, params, url, category)

                else:
                    logger.info("[launcher.py] executing channel '"+action+"' method")
                    if action!="findvideos":
                        exec "itemlist = channel."+action+"(item)"
                    else:
                        # Intenta ejecutar una posible funcion "findvideos" del canal
                        try:
                            exec "itemlist = channel."+action+"(item)"
                        # Si no funciona, lanza el método genérico para detectar vídeos
                        except:
                            logger.info("[launcher.py] no channel 'findvideos' method, executing core method")
                            from servers import servertools
                            itemlist = servertools.find_video_items(item)
                        from core import subtitletools
                        subtitletools.saveSubtitleName(item)

                    # Activa el modo biblioteca para todos los canales genéricos, para que se vea el argumento
                    import xbmcplugin
                    import sys
                    handle = sys.argv[1]
                    xbmcplugin.setContent(int( handle ),"movies")
                    
                    # Añade los items a la lista de XBMC
                    xbmctools.renderItems(itemlist, params, url, category)

    except urllib2.URLError,e:
        import traceback
        import sys
        from pprint import pprint
        exc_type, exc_value, exc_tb = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_tb)
        for line in lines:
            line_splits = line.split("\n")
            for line_split in line_splits:
                logger.error(line_split)
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

# Parse XBMC params - based on script.module.parsedom addon    
def get_params():
    logger.info("get_params")
    
    param_string = sys.argv[2]
    
    logger.info("get_params "+str(param_string))
    
    commands = {}

    if param_string:
        split_commands = param_string[param_string.find('?') + 1:].split('&')
    
        for command in split_commands:
            logger.info("get_params command="+str(command))
            if len(command) > 0:
                if "=" in command:
                    split_command = command.split('=')
                    key = split_command[0]
                    value = urllib.unquote_plus(split_command[1])
                    commands[key] = value
                else:
                    commands[command] = ""
    
    logger.info("get_params "+repr(commands))
    return commands

# Extract parameters from sys.argv
def extract_parameters():
    logger.info("[launcher.py] extract_parameters")
    #Imprime en el log los parámetros de entrada
    logger.info("[launcher.py] sys.argv=%s" % str(sys.argv))
    
    # Crea el diccionario de parametros
    #params = dict()
    #if len(sys.argv)>=2 and len(sys.argv[2])>0:
    #    params = dict(part.split('=') for part in sys.argv[ 2 ][ 1: ].split('&'))
    params = get_params()
    logger.info("[launcher.py] params=%s" % str(params))

    if (params.has_key("channel")):
        channel = urllib.unquote_plus( params.get("channel") )
    else:
        channel=''
    
    # Extrae la url de la página
    if (params.has_key("url")):
        url = urllib.unquote_plus( params.get("url") )
    else:
        url=''

    # Extrae la accion
    if (params.has_key("action")):
        action = params.get("action")
    else:
        action = "selectchannel"

    # Extrae el server
    if (params.has_key("server")):
        server = params.get("server")
    else:
        server = ""

    # Extrae la categoria
    if (params.has_key("category")):
        category = urllib.unquote_plus( params.get("category") )
    else:
        if params.has_key("channel"):
            category = params.get("channel")
        else:
            category = ""
            
    # Extrae el título de la serie
    if (params.has_key("show")):
        show = params.get("show")
    else:
        show = ""

    # Extrae el título del video
    if params.has_key("title"):
        title = urllib.unquote_plus( params.get("title") )
    else:
        title = ""

    # Extrae el título del video
    if params.has_key("channel_title"):
        channel_title = urllib.unquote_plus( params.get("channel_title") )
    else:
        channel_title = ""

    # Extrae el título del video
    if params.has_key("show_title"):
        show_title = urllib.unquote_plus( params.get("show_title") )
    else:
        show_title = ""

    # Extrae el título del video
    if params.has_key("fulltitle"):
        fulltitle = urllib.unquote_plus( params.get("fulltitle") )
    else:
        fulltitle = ""

    if params.has_key("thumbnail"):
        thumbnail = urllib.unquote_plus( params.get("thumbnail") )
    else:
        thumbnail = ""

    if params.has_key("plot"):
        plot = urllib.unquote_plus( params.get("plot") )
    else:
        plot = ""

    if params.has_key("uid"):
        uid = urllib.unquote_plus( params.get("uid") )
    else:
        uid = ""

    if params.has_key("extradata"):
        extra = urllib.unquote_plus( params.get("extradata") )
    else:
        extra = ""

    if params.has_key("subtitle"):
        subtitle = urllib.unquote_plus( params.get("subtitle") )
    else:
        subtitle = ""

    if params.has_key("password"):
        password = urllib.unquote_plus( params.get("password") )
    else:
        password = ""

    if params.has_key("show"):
        show = urllib.unquote_plus( params.get("show") )
    else:
        if params.has_key("Serie"):
            show = urllib.unquote_plus( params.get("Serie") )
        else:
            show = ""

    return params, channel, title, channel_title, show_title, fulltitle, url, thumbnail, plot, uid, action, server, extra, subtitle, category, show, password

def download_all_episodes(item,channel=None,first_episode="", silent=False):
    logger.info("[launcher.py] download_all_episodes, show="+item.show+" item="+item.tostring())

    item.show = item.show.replace("[COLOR yellow]","")
    item.show = item.show.replace("[/COLOR]","")

    from servers import servertools
    from core import downloadtools
    from core import scrapertools

    show_title = downloadtools.limpia_nombre_caracteres_especiales(item.show)

    # Obtiene el listado desde el que se llamó
    action = item.action

    if channel is None:
        exec "import channels."+item.channel+" as channel"

    exec "episode_itemlist = channel."+action+"(item)"

    best_server = "streamcloud"
    worst_server = "moevideos"

    # Para cada episodio
    if first_episode=="":
        empezar = True
    else:
        empezar = False

    for episode_item in episode_itemlist:
        # Si XBMC se está cerrando, cancela
        try:
            if xbmc.abortRequested:
                logger.error( "[launcher.py] download_all_episodes XBMC Abort requested" )
                return -1
        except:
            pass

        # Si es la opción de descargar, la de "Opciones de la serie" o la de paginación, las ignora
        if episode_item.action.startswith("download_all_episodes") or episode_item.action.startswith("serie_options") or episode_item.action.startswith(action):
            continue

        logger.info("[launcher.py] download_all_episodes, episode="+episode_item.title)
        try:
            episode_title = scrapertools.get_match(episode_item.title,"(\d+x\d+)")
        except:
            episode_title = episode_item.title

        if item.channel=="rtve":
            import re
            episode_title = re.compile("\(.*?\)",re.DOTALL).sub("",episode_title).strip()

        logger.info("[launcher.py] download_all_episodes, episode="+episode_title)

        if first_episode!="" and episode_title==first_episode:
            empezar = True

        if not empezar:
            continue

        try:
            # Extrae los mirrors
            mirrors_itemlist = [episode_item] #channel.findvideos(episode_item)

            descargado = False

            new_mirror_itemlist_1 = []
            new_mirror_itemlist_2 = []
            new_mirror_itemlist_3 = []
            new_mirror_itemlist_4 = []
            new_mirror_itemlist_5 = []
            new_mirror_itemlist_6 = []

            for mirror_item in mirrors_itemlist:
                
                # Si está en español va al principio, si no va al final
                if "(Español)" in mirror_item.title:
                    if best_server in mirror_item.title.lower():
                        new_mirror_itemlist_1.append(mirror_item)
                    else:
                        new_mirror_itemlist_2.append(mirror_item)
                elif "(VOS)" in mirror_item.title:
                    if best_server in mirror_item.title.lower():
                        new_mirror_itemlist_3.append(mirror_item)
                    else:
                        new_mirror_itemlist_4.append(mirror_item)
                else:
                    if best_server in mirror_item.title.lower():
                        new_mirror_itemlist_5.append(mirror_item)
                    else:
                        new_mirror_itemlist_6.append(mirror_item)

            mirrors_itemlist = new_mirror_itemlist_1 + new_mirror_itemlist_2 + new_mirror_itemlist_3 + new_mirror_itemlist_4 + new_mirror_itemlist_5 + new_mirror_itemlist_6

            for mirror_item in mirrors_itemlist:
                logger.info("[launcher.py] download_all_episodes, mirror="+mirror_item.title)

                if "(Español)" in mirror_item.title:
                    idioma=" (Español)"
                elif "(VOS)" in mirror_item.title:
                    idioma=" (VOS)"
                elif "(VO)" in mirror_item.title:
                    idioma=" (VO)"
                else:
                    idioma=""
                logger.info("[launcher.py] download_all_episodes, downloading mirror")

                if hasattr(channel, 'play'):
                    video_items = channel.play(mirror_item)
                else:
                    video_items = [mirror_item]

                if len(video_items)>0 and not downloadtools.is_in_download_history(video_items[0].url):
                    video_item = video_items[0]

                    # Comprueba que esté disponible
                    video_urls, puedes, motivo = servertools.resolve_video_urls_for_playing( video_item.server , video_item.url , video_password="" , muestra_dialogo=False)

                    # Lo añade a la lista de descargas
                    if puedes:
                        logger.info("[launcher.py] download_all_episodes, downloading mirror started...")
                        
                        # El vídeo de más calidad es el primero
                        mediaurl = video_urls[0][1]

                        if video_item.server=="descargavideos":
                            from servers import descargavideos
                            filetitle = show_title+" "+episode_title+idioma+" ["+descargavideos.get_real_server_name(video_item.url)+"]"
                        elif video_item.server!="directo":
                            filetitle = show_title+" "+episode_title+idioma+" ["+video_item.server+"]"
                        else:
                            filetitle = show_title+" "+episode_title+idioma+" ["+item.channel+"]"

                        # Descarga el vídeo
                        show_folder = os.path.join( config.get_setting("downloadpath") , show_title)
                        if not os.path.exists(show_folder):
                            os.mkdir(show_folder)

                        # Genera el NFO
                        try:
                            nfofilepath = downloadtools.getfilefromtitle("sample.nfo",filetitle,folder=show_title)
                            outfile = open(nfofilepath,"w")
                            outfile.write("<movie>\n")
                            outfile.write("<title>("+filetitle+")</title>\n")
                            outfile.write("<originaltitle></originaltitle>\n")
                            outfile.write("<rating>0.000000</rating>\n")
                            outfile.write("<year>2009</year>\n")
                            outfile.write("<top250>0</top250>\n")
                            outfile.write("<votes>0</votes>\n")
                            outfile.write("<outline></outline>\n")
                            outfile.write("<plot>"+episode_item.plot+"</plot>\n")
                            outfile.write("<tagline></tagline>\n")
                            outfile.write("<runtime></runtime>\n")
                            outfile.write("<thumb></thumb>\n")
                            outfile.write("<mpaa>Not available</mpaa>\n")
                            outfile.write("<playcount>0</playcount>\n")
                            outfile.write("<watched>false</watched>\n")
                            outfile.write("<id>tt0432337</id>\n")
                            outfile.write("<filenameandpath></filenameandpath>\n")
                            outfile.write("<trailer></trailer>\n")
                            outfile.write("<genre></genre>\n")
                            outfile.write("<credits></credits>\n")
                            outfile.write("<director></director>\n")
                            outfile.write("<actor>\n")
                            outfile.write("<name></name>\n")
                            outfile.write("<role></role>\n")
                            outfile.write("</actor>\n")
                            outfile.write("</movie>")
                            outfile.flush()
                            outfile.close()
                            logger.info("core.descargas Creado fichero NFO")
                        except:
                            logger.info("core.descargas Error al crear NFO")
                            for line in sys.exc_info():
                                logger.error( "%s" % line )

                        # Descarga el thumbnail
                        if episode_item.thumbnail != "":
                           logger.info("core.descargas thumbnail="+episode_item.thumbnail)
                           thumbnailfile = downloadtools.getfilefromtitle(episode_item.thumbnail,filetitle,folder=show_title)
                           thumbnailfile = thumbnailfile[:-4] + ".tbn"
                           logger.info("core.descargas thumbnailfile="+thumbnailfile)
                           try:
                               downloadtools.downloadfile(episode_item.thumbnail,thumbnailfile)
                               logger.info("core.descargas Thumbnail descargado")
                           except:
                               logger.info("core.descargas error al descargar thumbnail")
                               for line in sys.exc_info():
                                   logger.error( "%s" % line )

                        devuelve = downloadtools.downloadbest(video_urls,filetitle,continuar=True,silent=silent,folder=show_title)

                        if devuelve==0:
                            logger.info("[launcher.py] download_all_episodes, download ok")
                            descargado = True
                            downloadtools.add_to_download_history(video_item.url,filetitle)
                            break
                        elif devuelve==-1:
                            try:
                                import xbmcgui
                                advertencia = xbmcgui.Dialog()
                                resultado = advertencia.ok("plugin" , "Descarga abortada")
                            except:
                                pass
                            return
                        else:
                            logger.info("[launcher.py] download_all_episodes, download error, try another mirror")
                            break

                    else:
                        logger.info("[launcher.py] download_all_episodes, downloading mirror not available... trying next")

            if not descargado:
                logger.info("[launcher.py] download_all_episodes, EPISODIO NO DESCARGADO "+episode_title)
        except:
           logger.info("core.descargas error no controlado al descargar episodio")
           for line in sys.exc_info():
               logger.error( "%s" % line )
