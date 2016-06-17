# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Lista de v?eos favoritos
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
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

CHANNELNAME = "favoritos"
DEBUG = True
BOOKMARK_PATH = config.get_setting( "bookmarkpath" )

if not BOOKMARK_PATH.upper().startswith("SMB://"):
    if BOOKMARK_PATH=="":
        BOOKMARK_PATH = os.path.join( config.get_data_path() , "bookmarks" )
    if not os.path.exists(BOOKMARK_PATH):
        logger.debug("[favoritos.py] Path de bookmarks no existe, se crea: "+BOOKMARK_PATH)
        os.mkdir(BOOKMARK_PATH)

logger.info("tvalacarta.core.favoritos path="+BOOKMARK_PATH)

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.core.favoritos mainlist")
    itemlist=[]

    itemlist.append( Item(channel="api_programas", action="get_favorite_programs" , title="Programas", view="programs"))
    itemlist.append( Item(channel=CHANNELNAME, action="get_all_videos" , title="Vídeos", view="videos"))

    return itemlist

def get_all_videos(item):
    logger.info("tvalacarta.core.favoritos get_all_videos")
    itemlist=[]

    # Crea un listado con las entradas de favoritos
    if usingsamba(BOOKMARK_PATH):
        ficheros = samba.get_files(BOOKMARK_PATH)
    else:
        ficheros = os.listdir(BOOKMARK_PATH)
    
    # Ordena el listado por nombre de fichero (orden de incorporaci?)
    ficheros.sort()
    
    # Rellena el listado
    for fichero in ficheros:

        try:
            # Lee el bookmark
            canal,titulo,thumbnail,plot,server,url,fulltitle = readbookmark(fichero)
            if canal=="":
                canal="favoritos"

            # Crea la entrada
            # En extra va el nombre del fichero para poder borrarlo
            ## <-- A?do fulltitle con el titulo de la peli
            if server=="":
                itemlist.append( Item( channel=canal , action="play" , url=url , server=server, title=fulltitle, thumbnail=thumbnail, plot=plot, fanart=thumbnail, extra=os.path.join( BOOKMARK_PATH, fichero ), fulltitle=fulltitle, folder=False ))
            else:
                itemlist.append( Item( channel=canal , action="play" , url=url , server=server, title=fulltitle, thumbnail=thumbnail, plot=plot, fanart=thumbnail, extra=os.path.join( BOOKMARK_PATH, fichero ), fulltitle=fulltitle, folder=False ))
        except:
            for line in sys.exc_info():
                logger.error( "%s" % line )
    
    return itemlist

def readbookmark(filename,readpath=BOOKMARK_PATH):
    logger.info("tvalacarta.core.favoritos readbookmark")

    if usingsamba(readpath):
        bookmarkfile = samba.get_file_handle_for_reading(filename, readpath)
    else:
        filepath = os.path.join( readpath , filename )

        # Lee el fichero de configuracion
        logger.info("tvalacarta.core.favoritos filepath="+filepath)
        bookmarkfile = open(filepath)
    lines = bookmarkfile.readlines()

    try:
        titulo = urllib.unquote_plus(lines[0].strip())
    except:
        titulo = lines[0].strip()
    
    try:
        url = urllib.unquote_plus(lines[1].strip())
    except:
        url = lines[1].strip()
    
    try:
        thumbnail = urllib.unquote_plus(lines[2].strip())
    except:
        thumbnail = lines[2].strip()
    
    try:
        server = urllib.unquote_plus(lines[3].strip())
    except:
        server = lines[3].strip()
        
    try:
        plot = urllib.unquote_plus(lines[4].strip())
    except:
        plot = lines[4].strip()

    ## Campos fulltitle y canal a?didos
    if len(lines)>=6:
        try:
            fulltitle = urllib.unquote_plus(lines[5].strip())
        except:
            fulltitle = lines[5].strip()
    else:
        fulltitle=titulo

    if len(lines)>=7:
        try:
            canal = urllib.unquote_plus(lines[6].strip())
        except:
            canal = lines[6].strip()
    else:
        canal=""

    bookmarkfile.close();

    return canal,titulo,thumbnail,plot,server,url,fulltitle

def savebookmark(canal=CHANNELNAME,titulo="",url="",thumbnail="",server="",plot="",fulltitle="",savepath=BOOKMARK_PATH):
    logger.info("tvalacarta.core.favoritos savebookmark(path="+savepath+")")

    # Crea el directorio de favoritos si no existe
    if not usingsamba(savepath):
        try:
            os.mkdir(savepath)
        except:
            pass

    # Lee todos los ficheros
    if usingsamba(savepath):
        ficheros = samba.get_files(savepath)
    else:
        ficheros = os.listdir(savepath)
    ficheros.sort()
    
    # Averigua el ?ltimo n?mero
    if len(ficheros)>0:
        # XRJ: Linea problem?ica, sustituida por el bucle siguiente
        #filenumber = int( ficheros[len(ficheros)-1][0:-4] )+1
        filenumber = 1
        for fichero in ficheros:
            logger.info("tvalacarta.core.favoritos fichero="+fichero)
            try:
                tmpfilenumber = int( fichero[0:8] )+1
                if tmpfilenumber > filenumber:
                    filenumber = tmpfilenumber
            except:
                pass
    else:
        filenumber=1

    # Genera el contenido
    filecontent = ""
    filecontent = filecontent + urllib.quote_plus(downloadtools.limpia_nombre_excepto_1(titulo))+'\n'
    filecontent = filecontent + urllib.quote_plus(url)+'\n'
    filecontent = filecontent + urllib.quote_plus(thumbnail)+'\n'
    filecontent = filecontent + urllib.quote_plus(server)+'\n'
    filecontent = filecontent + urllib.quote_plus(downloadtools.limpia_nombre_excepto_1(plot))+'\n'
    filecontent = filecontent + urllib.quote_plus(fulltitle)+'\n'
    filecontent = filecontent + urllib.quote_plus(canal)+'\n'

    # Genera el nombre de fichero
    from core import scrapertools
    filename = '%08d-%s.txt' % (filenumber,scrapertools.slugify(fulltitle))
    logger.info("tvalacarta.core.favoritos savebookmark filename="+filename)

    # Graba el fichero
    if not usingsamba(savepath):
        fullfilename = os.path.join(savepath,filename)
        bookmarkfile = open(fullfilename,"w")
        bookmarkfile.write(filecontent)
        bookmarkfile.flush();
        bookmarkfile.close()
    else:
        samba.write_file(filename, filecontent, savepath)

def deletebookmark(fullfilename,deletepath=BOOKMARK_PATH):
    logger.info("tvalacarta.core.favoritos deletebookmark(fullfilename="+fullfilename+",deletepath="+deletepath+")")

    if not usingsamba(deletepath):
        os.remove( os.path.join( urllib.unquote_plus( deletepath ) , urllib.unquote_plus( fullfilename )))
    else:
        fullfilename = fullfilename.replace("\\","/")
        partes = fullfilename.split("/")
        filename = partes[len(partes)-1]
        logger.info("tvalacarta.core.favoritos filename="+filename)
        logger.info("tvalacarta.core.favoritos deletepath="+deletepath)
        samba.remove_file(filename,deletepath)

def usingsamba(path):
    return path.upper().startswith("SMB://")
