# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta
# XBMC Plugin
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os
import sys
import scrapertools
import time
import config
import logger
import api

# FIXME: Esto está repetido en el channelselector, debería ir a config
thumbnail_type = config.get_setting("thumbnail_type")
if thumbnail_type=="":
    thumbnail_type="2"
logger.info("thumbnail_type="+thumbnail_type)
if thumbnail_type=="0":
    IMAGES_PATH = 'http://media.tvalacarta.info/tvalacarta/posters/'
elif thumbnail_type=="1":
    IMAGES_PATH = 'http://media.tvalacarta.info/tvalacarta/banners/'
elif thumbnail_type=="2":
    IMAGES_PATH = 'http://media.tvalacarta.info/tvalacarta/squares/'

ROOT_DIR = config.get_runtime_path()

REMOTE_VERSION_FILE = "http://descargas.tvalacarta.info/"+config.PLUGIN_NAME+"-version.xml"
LOCAL_VERSION_FILE = os.path.join( ROOT_DIR , "version.xml" )
LOCAL_FILE = os.path.join( ROOT_DIR , config.PLUGIN_NAME+"-" )

try:
    # Añadida a la opcion : si plataforma xbmcdharma es "True", no debe ser con la plataforma de la xbox
    # porque seria un falso "True", ya que el xbmc en las xbox no son dharma por lo tanto no existen los addons
    logger.info("tvalacarta.core.updater get_platform="+config.get_platform())
    logger.info("tvalacarta.core.updater get_system_platform="+config.get_system_platform())
    if config.get_platform()=="kodi-krypton":
        import xbmc
        REMOTE_FILE = "http://descargas.tvalacarta.info/"+config.PLUGIN_NAME+"-kodi-krypton-"
        DESTINATION_FOLDER = xbmc.translatePath( "special://home/addons")
    elif config.get_platform()=="kodi-jarvis":
        import xbmc
        REMOTE_FILE = "http://descargas.tvalacarta.info/"+config.PLUGIN_NAME+"-kodi-jarvis-"
        DESTINATION_FOLDER = xbmc.translatePath( "special://home/addons")
    elif config.get_platform()=="kodi-isengard":
        import xbmc
        REMOTE_FILE = "http://descargas.tvalacarta.info/"+config.PLUGIN_NAME+"-kodi-isengard-"
        DESTINATION_FOLDER = xbmc.translatePath( "special://home/addons")
    elif config.get_platform()=="kodi-helix":
        import xbmc
        REMOTE_FILE = "http://descargas.tvalacarta.info/"+config.PLUGIN_NAME+"-kodi-helix-"
        DESTINATION_FOLDER = xbmc.translatePath( "special://home/addons")
    elif config.get_platform()=="xbmc-eden":
        import xbmc
        REMOTE_FILE = "http://descargas.tvalacarta.info/"+config.PLUGIN_NAME+"-xbmc-eden-"
        DESTINATION_FOLDER = xbmc.translatePath( "special://home/addons")
    elif config.get_platform()=="xbmc-frodo":
        import xbmc
        REMOTE_FILE = "http://descargas.tvalacarta.info/"+config.PLUGIN_NAME+"-xbmc-frodo-"
        DESTINATION_FOLDER = xbmc.translatePath( "special://home/addons")
    elif config.get_platform()=="xbmc-gotham":
        import xbmc
        REMOTE_FILE = "http://descargas.tvalacarta.info/"+config.PLUGIN_NAME+"-xbmc-gotham-"
        DESTINATION_FOLDER = xbmc.translatePath( "special://home/addons")
    elif config.get_platform()=="xbmc":
        import xbmc
        REMOTE_FILE = "http://descargas.tvalacarta.info/"+config.PLUGIN_NAME+"-xbmc-plugin-"
        DESTINATION_FOLDER = xbmc.translatePath( "special://home/plugins/video")
    elif config.get_platform()=="wiimc":
        REMOTE_FILE = "http://descargas.tvalacarta.info/"+config.PLUGIN_NAME+"-wiimc-"
        DESTINATION_FOLDER = os.path.join(config.get_runtime_path(),"..")
    elif config.get_platform()=="rss":
        REMOTE_FILE = "http://descargas.tvalacarta.info/"+config.PLUGIN_NAME+"-rss-"
        DESTINATION_FOLDER = os.path.join(config.get_runtime_path(),"..")

except:
    import xbmc
    REMOTE_FILE = "http://descargas.tvalacarta.info/"+config.PLUGIN_NAME+"-xbmc-plugin-"
    DESTINATION_FOLDER = xbmc.translatePath( os.path.join( ROOT_DIR , ".." ) )

def checkforupdates(plugin_mode=True):
    logger.info("tvalacarta.core.updater checkforupdates")

    # Descarga el fichero con la versión en la web
    logger.info("tvalacarta.core.updater Verificando actualizaciones...")
    logger.info("tvalacarta.core.updater Version remota: "+REMOTE_VERSION_FILE)
    data = scrapertools.cachePage( REMOTE_VERSION_FILE )

    '''    
    <?xml version="1.0" encoding="utf-8" standalone="yes"?>
    <version>
            <name>tvalacarta</name>
            <tag>4.0     </tag>
            <version>4000</tag>
            <date>20/03/2015</date>
            <changes>New release</changes>
    </version>
    '''

    version_publicada = scrapertools.find_single_match(data,"<version>([^<]+)</version>").strip()
    tag_publicada = scrapertools.find_single_match(data,"<tag>([^<]+)</tag>").strip()
    logger.info("tvalacarta.core.updater version remota="+tag_publicada+" "+version_publicada)
    
    # Lee el fichero con la versión instalada
    localFileName = LOCAL_VERSION_FILE
    logger.info("tvalacarta.core.updater fichero local version: "+localFileName)
    infile = open( localFileName )
    data = infile.read()
    infile.close();
    #logger.info("xml local="+data)

    version_local = scrapertools.find_single_match(data,"<version>([^<]+)</version>").strip()
    tag_local = scrapertools.find_single_match(data,"<tag>([^<]+)</tag>").strip()
    logger.info("tvalacarta.core.updater version local="+tag_local+" "+version_local)

    try:
        numero_version_publicada = int(version_publicada)
        numero_version_local = int(version_local)
    except:
        import traceback
        logger.info(traceback.format_exc())
        version_publicada = ""
        version_local = ""

    if version_publicada=="" or version_local=="":
        arraydescargada = tag_publicada.split(".")
        arraylocal = tag_local.split(".")

        # local 2.8.0 - descargada 2.8.0 -> no descargar
        # local 2.9.0 - descargada 2.8.0 -> no descargar
        # local 2.8.0 - descargada 2.9.0 -> descargar
        if len(arraylocal) == len(arraydescargada):
            logger.info("caso 1")
            hayqueactualizar = False
            for i in range(0, len(arraylocal)):
                print arraylocal[i], arraydescargada[i], int(arraydescargada[i]) > int(arraylocal[i])
                if int(arraydescargada[i]) > int(arraylocal[i]):
                    hayqueactualizar = True
        # local 2.8.0 - descargada 2.8 -> no descargar
        # local 2.9.0 - descargada 2.8 -> no descargar
        # local 2.8.0 - descargada 2.9 -> descargar
        if len(arraylocal) > len(arraydescargada):
            logger.info("caso 2")
            hayqueactualizar = False
            for i in range(0, len(arraydescargada)):
                #print arraylocal[i], arraydescargada[i], int(arraydescargada[i]) > int(arraylocal[i])
                if int(arraydescargada[i]) > int(arraylocal[i]):
                    hayqueactualizar = True
        # local 2.8 - descargada 2.8.8 -> descargar
        # local 2.9 - descargada 2.8.8 -> no descargar
        # local 2.10 - descargada 2.9.9 -> no descargar
        # local 2.5 - descargada 3.0.0
        if len(arraylocal) < len(arraydescargada):
            logger.info("caso 3")
            hayqueactualizar = True
            for i in range(0, len(arraylocal)):
                #print arraylocal[i], arraydescargada[i], int(arraylocal[i])>int(arraydescargada[i])
                if int(arraylocal[i]) > int(arraydescargada[i]):
                    hayqueactualizar =  False
                elif int(arraylocal[i]) < int(arraydescargada[i]):
                    hayqueactualizar =  True
                    break
    else:
        hayqueactualizar = (numero_version_publicada > numero_version_local)

    if hayqueactualizar:
    
        if plugin_mode:
    
            logger.info("tvalacarta.core.updater actualizacion disponible")
            
            # Añade al listado de XBMC
            import xbmcgui
            thumbnail = IMAGES_PATH+"Crystal_Clear_action_info.png"
            logger.info("thumbnail="+thumbnail)
            listitem = xbmcgui.ListItem( "Descargar version "+tag_publicada, thumbnailImage=thumbnail )
            itemurl = '%s?action=update&version=%s' % ( sys.argv[ 0 ] , tag_publicada )
            import xbmcplugin
            xbmcplugin.addDirectoryItem( handle = int(sys.argv[ 1 ]), url = itemurl , listitem=listitem, isFolder=True)
            
            # Avisa con un popup
            dialog = xbmcgui.Dialog()
            dialog.ok("Versión "+tag_publicada+" disponible","Ya puedes descargar la nueva versión del plugin\ndesde el listado principal")

        else:

            import xbmcgui
            yes_pressed = xbmcgui.Dialog().yesno( "Versión "+tag_publicada+" disponible" , "¿Quieres instalarla?" )

            if yes_pressed:
                update( Item(version=tag_publicada) )

    '''
    except:
        logger.info("No se han podido verificar actualizaciones...")
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
    '''
def update(item):
    # Descarga el ZIP
    logger.info("tvalacarta.core.updater update")
    remotefilename = REMOTE_FILE+item.version+".zip"
    localfilename = LOCAL_FILE+item.version+".zip"
    logger.info("tvalacarta.core.updater remotefilename=%s" % remotefilename)
    logger.info("tvalacarta.core.updater localfilename=%s" % localfilename)
    logger.info("tvalacarta.core.updater descarga fichero...")
    inicio = time.clock()
    
    #urllib.urlretrieve(remotefilename,localfilename)
    from core import downloadtools
    downloadtools.downloadfile(remotefilename, localfilename, continuar=False)
    
    fin = time.clock()
    logger.info("tvalacarta.core.updater Descargado en %d segundos " % (fin-inicio+1))
    
    # Lo descomprime
    logger.info("tvalacarta.core.updater descomprime fichero...")
    import ziptools
    unzipper = ziptools.ziptools()
    destpathname = DESTINATION_FOLDER
    logger.info("tvalacarta.core.updater destpathname=%s" % destpathname)
    unzipper.extract(localfilename,destpathname)
    
    # Borra el zip descargado
    logger.info("tvalacarta.core.updater borra fichero...")
    os.remove(localfilename)
    logger.info("tvalacarta.core.updater ...fichero borrado")

def get_channel_remote_url(channel_name):

    _remote_channel_url_ = "https://raw.githubusercontent.com/tvalacarta/tvalacarta/master/python/main-classic/"

    if channel_name <> "channelselector":
        _remote_channel_url_+= "channels/"

    remote_channel_url = _remote_channel_url_+channel_name+".py"
    remote_version_url = _remote_channel_url_+channel_name+".xml" 

    logger.info("tvalacarta.core.updater remote_channel_url="+remote_channel_url)
    logger.info("tvalacarta.core.updater remote_version_url="+remote_version_url)
    
    return remote_channel_url , remote_version_url

def get_channel_local_path(channel_name):
    # TODO: (3.2) El XML debería escribirse en el userdata, de forma que se leerán dos ficheros locales: el del userdata y el que está junto al py (vendrá con el plugin). El mayor de los 2 es la versión actual, y si no existe fichero se asume versión 0
    if channel_name<>"channelselector":
        local_channel_path = os.path.join( config.get_runtime_path() , 'channels' , channel_name+".py" )
        local_version_path = os.path.join( config.get_runtime_path() , 'channels' , channel_name+".xml" )
        local_compiled_path = os.path.join( config.get_runtime_path() , 'channels' , channel_name+".pyo" )
    else:
        local_channel_path = os.path.join( config.get_runtime_path() , channel_name+".py" )
        local_version_path = os.path.join( config.get_runtime_path() , channel_name+".xml" )
        local_compiled_path = os.path.join( config.get_runtime_path() , channel_name+".pyo" )

    logger.info("tvalacarta.core.updater local_channel_path="+local_channel_path)
    logger.info("tvalacarta.core.updater local_version_path="+local_version_path)
    logger.info("tvalacarta.core.updater local_compiled_path="+local_compiled_path)
    
    return local_channel_path , local_version_path , local_compiled_path

def updatechannel(channel_name):
    logger.info("tvalacarta.core.updater updatechannel('"+channel_name+"')")
    
    # Canal remoto
    remote_channel_url , remote_version_url = get_channel_remote_url(channel_name)
    
    # Canal local
    local_channel_path , local_version_path , local_compiled_path = get_channel_local_path(channel_name)
    
    #if not os.path.exists(local_channel_path):
    #    return False;

    # Version remota
    try:
        data = scrapertools.cachePage( remote_version_url )
        logger.info("tvalacarta.core.updater remote_data="+data)
        
        if "<tag>" in data: 
            patronvideos  = '<tag>([^<]+)</tag>'
        elif "<version>" in data: 
            patronvideos  = '<version>([^<]+)</version>'

        matches = re.compile(patronvideos,re.DOTALL).findall(data)
        remote_version = int(matches[0])
    except:
        remote_version = 0

    logger.info("tvalacarta.core.updater remote_version=%d" % remote_version)

    # Version local
    if os.path.exists( local_version_path ):
        infile = open( local_version_path )
        data = infile.read()
        infile.close();
        logger.info("tvalacarta.core.updater local_data="+data)

        if "<tag>" in data:
            patronvideos  = '<tag>([^<]+)</tag>'
        elif "<version>" in data:
            patronvideos  = '<version>([^<]+)</version>' 

        matches = re.compile(patronvideos,re.DOTALL).findall(data)
        local_version = int(matches[0])
    else:
        local_version = 0
    
    logger.info("tvalacarta.core.updater local_version=%d" % local_version)
    
    # Comprueba si ha cambiado
    updated = remote_version > local_version

    if updated:
        logger.info("tvalacarta.core.updater updated")
        download_channel(channel_name)

    return updated

def download_channel(channel_name):
    logger.info("tvalacarta.core.updater download_channel('"+channel_name+"')")
    # Canal remoto
    remote_channel_url , remote_version_url = get_channel_remote_url(channel_name)
    
    # Canal local
    local_channel_path , local_version_path , local_compiled_path = get_channel_local_path(channel_name)

    # Descarga el canal
    updated_channel_data = scrapertools.cachePage( remote_channel_url )
    try:
        outfile = open(local_channel_path,"w")
        outfile.write(updated_channel_data)
        outfile.flush()
        outfile.close()
        logger.info("tvalacarta.core.updater Grabado a " + local_channel_path)
    except:
        logger.info("tvalacarta.core.updater Error al grabar " + local_channel_path)
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )

    # Descarga la version (puede no estar)
    try:
        updated_version_data = scrapertools.cachePage( remote_version_url )
        outfile = open(local_version_path,"w")
        outfile.write(updated_version_data)
        outfile.flush()
        outfile.close()
        logger.info("tvalacarta.core.updater Grabado a " + local_version_path)
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )

    if os.path.exists(local_compiled_path):
        os.remove(local_compiled_path)
