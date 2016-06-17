# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Lista de vídeos descargados
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os
import sys
import datetime

from core import config
from core import logger
from core import samba
from core.item import Item
from core import scrapertools
from core import downloadtools
from core import suscription

import favoritos

CHANNELNAME = "descargas"
DEBUG = True

DOWNLOAD_LIST_PATH = config.get_setting("downloadlistpath")
IMAGES_PATH = os.path.join( config.get_runtime_path(), 'resources' , 'images' )
ERROR_PATH = os.path.join( DOWNLOAD_LIST_PATH, 'error' )
usingsamba = DOWNLOAD_LIST_PATH.upper().startswith("SMB://")

def isGeneric():
    return True

def mainlist(item):
    logger.info("core.descargas mainlist")
    itemlist=[]

    # Lee la ruta de descargas
    downloadpath = config.get_setting("downloadpath")

    logger.info("core.descargas downloadpath=" + downloadpath)

    itemlist.append( Item( channel="descargas", action="ultimas_descargas", title="Últimas descargas"))
    itemlist.append( Item( channel="descargas", action="todas_las_descargas", title="Todas las descargas"))
    itemlist.append( Item( channel="descargas", action="administrar_suscripciones" , title="Administrar descargas automáticas"))
    itemlist.append( Item( channel="descargas", action="descargas_pendientes"    , title="Administrar lista manual de descargas"))

    return itemlist

def administrar_suscripciones(item):
    logger.info("core.descargas administrar_suscripciones")
    itemlist=[]

    current_suscriptions = suscription.get_current_suscriptions()
    for suscription_item in current_suscriptions:
        itemlist.append( Item( channel="descargas" , action="borrar_suscripcion" , url=suscription_item.url , title=suscription_item.title, thumbnail=suscription_item.thumbnail, plot=suscription_item.plot, fanart=suscription_item.thumbnail, folder=False ))

    if len(itemlist)==0 and config.is_xbmc():
        import xbmcgui
        xbmcgui.Dialog().ok( "No tienes descargas automáticas" , "Elige un programa con el menú contextual, y añádelo a descargas automáticas para que los vídeos se descarguen solos a medida que se vayan publicando.")

    return itemlist

def borrar_suscripcion(item):
    logger.info("core.descargas borrar_suscripcion")

    import xbmcgui
    yes_pressed = xbmcgui.Dialog().yesno( "tvalacarta" , "¿Quieres cancelar la descarga automática de" , "\""+item.title+"\"?" )

    if yes_pressed:
        suscription.remove_suscription(item)
        import xbmc
        xbmc.executebuiltin( "Container.Refresh" )

def todas_las_descargas(item):
    logger.info("core.descargas todas_las_descargas")
    itemlist=[]

    ficheros_itemlist = get_all_downloads(path=item.url, recurse=False,sort_order="date")
    ficheros_itemlist.reverse()

    # Primero añade los directorios, luego los ficheros
    for descarga_item in ficheros_itemlist:
        if descarga_item.folder:
            itemlist.append( descarga_item )

    for descarga_item in ficheros_itemlist:
        if not descarga_item.folder:
            itemlist.append( descarga_item )

    return itemlist

def ultimas_descargas(item):
    logger.info("core.descargas ultimas_descargas")
    itemlist=[]

    ficheros_itemlist = get_all_downloads(recurse=True,sort_order="date")
    ficheros_itemlist.reverse()

    for descarga_item in ficheros_itemlist:
        itemlist.append( descarga_item )

    return itemlist

def get_all_downloads(path="", recurse=False, sort_order="filename"):
    logger.info("core.descargas get_recent_downloads")
    itemlist=[]

    if path=="":
        path = config.get_setting("downloadpath")

    ficheros = os.listdir(path)
    for fichero in ficheros:
        logger.info("core.descargas get_recent_downloads fichero=" + fichero+" "+repr(fichero.endswith(".nfo")))

        full_path = os.path.join( path , fichero )
        creation_timestamp = str(os.path.getctime(full_path))
        filesize = str(os.path.getsize(full_path))
        creation_date_formatted = datetime.datetime.fromtimestamp(os.path.getctime(full_path)).strftime('%Y-%m-%d %H:%M:%S')

        if not os.path.isdir(full_path):

            if fichero!=".DS_Store" and not fichero.endswith(".nfo") and not fichero.endswith(".tbn") and not fichero.endswith(".tmp"):

                plot = "Descargado en: "+creation_date_formatted+"\n"
                if os.path.exists(full_path[:-4]+".nfo"):
                    nfo_file = open(full_path[:-4]+".nfo")
                    nfo_data = nfo_file.read()
                    nfo_file.close()

                    plot = plot + scrapertools.find_single_match(nfo_data,"<plot>(.*?)</plot>")

                itemlist.append( Item( channel="descargas", action="play", title=fichero, thumbnail=full_path[:-4]+".tbn", fanart=full_path[:-4]+".tbn", fulltitle=fichero, url=full_path, plot=plot, extra=creation_timestamp, server="local", viewmode="movie_with_plot", size=filesize, folder=False))
        
        elif full_path!=config.get_setting("downloadlistpath"):

            if recurse:
                itemlist.extend( get_all_downloads(path=full_path,recurse=True))
            else:
                plot = ""
                itemlist.append( Item( channel="descargas", action="todas_las_descargas", title=fichero, thumbnail=full_path[:-4]+".tbn", fanart=full_path[:-4]+".tbn", fulltitle=fichero, url=full_path, plot=plot, extra=creation_timestamp, folder=True))

    if sort_order == "filename":
        itemlist = sorted(itemlist, key=lambda Item: Item.title) 
    elif sort_order == "date":
        itemlist = sorted(itemlist, key=lambda Item: float(Item.extra) )

    return itemlist

def descargas_pendientes(item):
    logger.info("core.descargas descargas_pendientes")
    itemlist=[]

    # Crea un listado con las entradas de favoritos
    if usingsamba:
        ficheros = samba.get_files(DOWNLOAD_LIST_PATH)
    else:
        ficheros = os.listdir(DOWNLOAD_LIST_PATH)

    # Ordena el listado por orden de incorporación
    ficheros.sort()
    
    # Crea un listado con las entradas de la lista de descargas
    for fichero in ficheros:
        logger.info("fichero="+fichero)
        try:
            # Lee el bookmark
            canal,titulo,thumbnail,plot,server,url,fulltitle = favoritos.readbookmark(fichero,DOWNLOAD_LIST_PATH)
            if canal=="":
                canal="descargas"

            logger.info("canal="+canal+", titulo="+titulo+", thumbnail="+thumbnail+", server="+server+", url="+url+", fulltitle="+fulltitle+", plot="+plot)

            # Crea la entrada
            # En la categoría va el nombre del fichero para poder borrarlo
            itemlist.append( Item( channel=canal , action="play" , url=url , server=server, title=titulo, fulltitle=fulltitle, thumbnail=thumbnail, plot=plot, fanart=thumbnail, extra=os.path.join( DOWNLOAD_LIST_PATH, fichero ), folder=False ))

        except:
            pass
            logger.info("core.descargas error al leer bookmark")
            for line in sys.exc_info():
                logger.error( "%s" % line )

    itemlist.append( Item( channel=CHANNELNAME , action="downloadall" , title="(Empezar la descarga de la lista)", thumbnail=os.path.join(IMAGES_PATH, "Crystal_Clear_action_db_update.png") , folder=False ))

    return itemlist

def downloadall(item):
    logger.info("core.descargas downloadall")

    # Lee la lista de ficheros
    if usingsamba:
        ficheros = samba.get_files(DOWNLOAD_LIST_PATH)
    else:
        ficheros = os.listdir(DOWNLOAD_LIST_PATH)

    logger.info("core.descargas numero de ficheros=%d" % len(ficheros))

    # La ordena
    ficheros.sort()
    
    # Crea un listado con las entradas de favoritos
    for fichero in ficheros:
        # El primer video de la lista
        logger.info("core.descargas fichero="+fichero)

        if fichero!="error" and fichero!=".DS_Store":
            # Descarga el vídeo
            try:
                # Lee el bookmark
                canal,titulo,thumbnail,plot,server,url,fulltitle = favoritos.readbookmark(fichero,DOWNLOAD_LIST_PATH)
                logger.info("core.descargas url="+url)

                # Averigua la URL del vídeo
                exec "from servers import "+server+" as server_connector"
                video_urls = server_connector.get_video_url( page_url=url , premium=(config.get_setting("megavideopremium")=="true") , user=config.get_setting("megavideouser") , password=config.get_setting("megavideopassword") )

                # La primera es la de mayor calidad, lo mejor para la descarga
                mediaurl = video_urls[0][1]
                logger.info("core.descargas mediaurl="+mediaurl)

                # Genera el NFO
                nfofilepath = downloadtools.getfilefromtitle("sample.nfo",fulltitle)
                outfile = open(nfofilepath,"w")
                outfile.write("<movie>\n")
                outfile.write("<title>("+fulltitle+")</title>\n")
                outfile.write("<originaltitle></originaltitle>\n")
                outfile.write("<rating>0.000000</rating>\n")
                outfile.write("<year>2009</year>\n")
                outfile.write("<top250>0</top250>\n")
                outfile.write("<votes>0</votes>\n")
                outfile.write("<outline></outline>\n")
                outfile.write("<plot>"+plot+"</plot>\n")
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
                
                # Descarga el thumbnail
                if thumbnail != "":
                   logger.info("core.descargas thumbnail="+thumbnail)
                   thumbnailfile = downloadtools.getfilefromtitle(thumbnail,fulltitle)
                   thumbnailfile = thumbnailfile[:-4] + ".tbn"
                   logger.info("core.descargas thumbnailfile="+thumbnailfile)
                   try:
                       downloadtools.downloadfile(thumbnail,thumbnailfile)
                       logger.info("core.descargas Thumbnail descargado")
                   except:
                       logger.info("core.descargas error al descargar thumbnail")
                       for line in sys.exc_info():
                           logger.error( "%s" % line )
                
                # Descarga el video
                dev = downloadtools.downloadtitle(mediaurl,fulltitle)
                if dev == -1:
                    # El usuario ha cancelado la descarga
                    logger.info("core.descargas Descarga cancelada")
                    return
                elif dev == -2:
                    # Error en la descarga, lo mueve a ERROR y continua con el siguiente
                    logger.info("core.descargas ERROR EN DESCARGA DE "+fichero)
                    if not usingsamba:
                        origen = os.path.join( DOWNLOAD_LIST_PATH , fichero )
                        destino = os.path.join( ERROR_PATH , fichero )
                        import shutil
                        shutil.move( origen , destino )
                    else:
                        favoritos.savebookmark(canal,titulo, url, thumbnail, server, plot, fulltitle, ERROR_PATH)
                        favoritos.deletebookmark(fichero, DOWNLOAD_LIST_PATH)
                else:
                    logger.info("core.descargas Video descargado")
                    # Borra el bookmark e itera para obtener el siguiente video
                    filepath = os.path.join( DOWNLOAD_LIST_PATH , fichero )
                    if usingsamba:
                        os.remove(filepath)
                    else:
                        favoritos.deletebookmark(fichero, DOWNLOAD_LIST_PATH)
                    logger.info("core.descargas "+fichero+" borrado")
            except:
                logger.info("core.descargas ERROR EN DESCARGA DE "+fichero)
                import sys
                for line in sys.exc_info():
                    logger.error( "%s" % line )
                if not usingsamba:
                    origen = os.path.join( DOWNLOAD_LIST_PATH , fichero )
                    destino = os.path.join( ERROR_PATH , fichero )
                    import shutil
                    shutil.move( origen , destino )
                else:
                    favoritos.savebookmark(canal,titulo, url, thumbnail, server, plot, fulltitle,ERROR_PATH)
                    favoritos.deletebookmark(fichero, DOWNLOAD_LIST_PATH)

    if config.is_xbmc():
        import xbmc
        xbmc.executebuiltin("XBMC.Container.Refresh()");    

def savebookmark(canal=CHANNELNAME,titulo="",url="",thumbnail="",server="",plot="",fulltitle="",savepath=DOWNLOAD_LIST_PATH):
    favoritos.savebookmark(canal,titulo,url,thumbnail,server,plot,fulltitle,savepath)

def deletebookmark(fullfilename,deletepath=DOWNLOAD_LIST_PATH):
    favoritos.deletebookmark(fullfilename,deletepath)

def delete_error_bookmark(fullfilename,deletepath=ERROR_PATH):
    favoritos.deletebookmark(fullfilename,deletepath)

def mover_descarga_error_a_pendiente(fullfilename):
    # La categoría es el nombre del fichero en favoritos, así que lee el fichero
    canal,titulo,thumbnail,plot,server,url,fulltitle = favoritos.readbookmark(fullfilename,"")
    # Lo añade a la lista de descargas
    savebookmark(canal,titulo,url,thumbnail,server,plot,fulltitle)
    # Y lo borra de la lista de errores
    os.remove(fullfilename)

#------------------------------------------------------------
# Context menu
#------------------------------------------------------------

def get_context_menu_for_item(item):

    context_commands = []

    if item.action == "borrar_suscripcion":
        context_commands.append( item.clone(command_title="Quitar de descargas automáticas", action="borrar_suscripcion") )

    return context_commands
