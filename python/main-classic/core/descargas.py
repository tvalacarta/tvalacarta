# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Lista de vídeos descargados
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os
import sys

from core import config
from core import logger
from core import samba
from core import favoritos
from core.item import Item
from core import scrapertools
from core import downloadtools
from core import suscription

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

    # Sólo para eden, frodo, gotham
    if config.is_xbmc():
        itemlist.append( Item( channel="descargas", action="suscripciones", title="Suscripciones", viewmode="movie_with_plot"))
    itemlist.append( Item( channel="descargas", action="pendientes", title="Descargas pendientes", viewmode="movie_with_plot"))
    itemlist.append( Item( channel="descargas", action="errores", title="Descargas con error"))

    # Añade al listado de XBMC
    try:
        ficheros = os.listdir(downloadpath)
        for fichero in ficheros:
            logger.info("core.descargas fichero=" + fichero)
            if fichero!="lista" and fichero!="error" and fichero!=".DS_Store" and not fichero.endswith(".nfo") and not fichero.endswith(".tbn") and os.path.join(downloadpath,fichero)!=config.get_setting("downloadlistpath"):
                url = os.path.join( downloadpath , fichero )

                try:
                    nfo_file = open(url[:-4]+".nfo")
                    nfo_data = nfo_file.read()
                    nfo_file.close()

                    plot = scrapertools.find_single_match(nfo_data,"<plot>(.*?)</plot>")
                except:
                    plot = ""

                if not os.path.isdir(url):
                    itemlist.append( Item( channel="descargas", action="play", title=fichero, thumbnail=url[:-4]+".tbn", fanart=url[:-4]+".tbn", fulltitle=fichero, url=url, plot=plot, server="local", folder=False))

    except:
        import traceback
        logger.info(traceback.format_exc())

    return itemlist

def suscripciones(item):
    logger.info("core.descargas suscripciones")
    itemlist=[]

    current_suscriptions = suscription.get_current_suscriptions()

    for suscription_item in current_suscriptions:
        itemlist.append( Item( channel="descargas" , action="borrar_suscripcion" , url=suscription_item.url , title=suscription_item.title, thumbnail=suscription_item.thumbnail, plot=suscription_item.plot, fanart=suscription_item.thumbnail, folder=False ))

    return itemlist

def borrar_suscripcion(item):

    import xbmcgui
    yes_pressed = xbmcgui.Dialog().yesno( "tvalacarta" , "¿Quieres eliminar tu suscripción a" , "\""+item.title+"\"?" )

    if yes_pressed:
        suscription.remove_suscription(item)
        import xbmc
        xbmc.executebuiltin( "Container.Refresh" )

def pendientes(item):
    logger.info("core.descargas pendientes")
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

def errores(item):
    logger.info("core.descargas errores")
    itemlist=[]

    # Crea un listado con las entradas de favoritos
    if usingsamba:
        ficheros = samba.get_files(ERROR_PATH)
    else:
        ficheros = os.listdir(ERROR_PATH)

    # Ordena el listado por orden de incorporación
    ficheros.sort()
    
    # Crea un listado con las entradas de la lista de descargas
    for fichero in ficheros:
        logger.info("core.descargas fichero="+fichero)
        try:
            # Lee el bookmark
            canal,titulo,thumbnail,plot,server,url,fulltitle = favoritos.readbookmark(fichero,ERROR_PATH)
            if canal=="":
                canal="descargas"

            # Crea la entrada
            # En la categoría va el nombre del fichero para poder borrarlo
            itemlist.append( Item( channel=canal , action="play" , url=url , server=server, title=titulo, fulltitle=fulltitle, thumbnail=thumbnail, plot=plot, fanart=thumbnail, category="errores", extra=os.path.join( ERROR_PATH, fichero ), folder=False ))

        except:
            pass
            logger.info("core.descargas error al leer bookmark")
            for line in sys.exc_info():
                logger.error( "%s" % line )

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

                if config.get_setting("fileniumpremium")=="true" and config.get_setting("filenium_for_download")=="true" and server not in ["vk","fourshared","directo","adnstream","facebook","megalive","tutv","stagevu"]:
                    exec "from servers import filenium as gen_conector"
                    
                    # Parche para solucionar el problema habitual de que un vídeo http://www.megavideo.com/?d=XXX no está, pero http://www.megaupload.com/?d=XXX si
                    url = url.replace("http://www.megavideo.com/?d","http://www.megaupload.com/?d")
        
                    video_gen = gen_conector.get_video_url( page_url=url , premium=(config.get_setting("fileniumpremium")=="true") , user=config.get_setting("fileniumuser") , password=config.get_setting("fileniumpassword") )
                    logger.info("[xbmctools.py] filenium url="+video_gen)
                    video_urls.append( [ "[filenium]", video_gen ] )

                # La última es la de mayor calidad, lo mejor para la descarga
                mediaurl = video_urls[ len(video_urls)-1 ][1]
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
