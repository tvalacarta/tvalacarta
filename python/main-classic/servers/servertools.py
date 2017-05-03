# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Utilidades para detectar vídeos de los diferentes conectores
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import re,sys

from core import scrapertools
from core import config
from core import logger

# Listas de servidores empleadas a la hora de reproducir para explicarle al usuario por qué no puede ver un vídeo

# Lista de los servidores que se pueden ver sin cuenta premium de ningún tipo
FREE_SERVERS = []
FREE_SERVERS.extend(['aragontv','rtve','xiptv'])
FREE_SERVERS.extend(['directo','allmyvideos','adnstream','bliptv','divxstage','downupload','facebook','fourshared'])
FREE_SERVERS.extend(['googlevideo','gigabyteupload','hdplay','filebox','mediafire','modovideo','movshare','novamov','ovfile','putlocker'])
FREE_SERVERS.extend(['rapidtube','royalvids','rutube','sockshare','stagevu','stagero','tutv','userporn','veoh','veevr','videobam'])
FREE_SERVERS.extend(['vidbux','videoweed','vidxden','vimeo','vk','watchfreeinhd','youtube','cartoonito','eitb','telemadrid','acbtv','mundonick','tv3','vuittv','dibujostv','tvn','mtv'])
FREE_SERVERS.extend(['boing','disneychannel','tvg','telefe','mitele','eltrece','extremaduratv','disneylatino','rtpa','cntv','conectate','telemundo','descargavideos','sieterm','rtvcm'])
FREE_SERVERS.extend(['upvtv','montecarlo','discoverymax','azteca','vtelevision','dwspan','pakapaka','onceninos','euronews','canal22','trececl','canal10','adn40'])

# Lista de TODOS los servidores que funcionan con cuenta premium individual
PREMIUM_SERVERS = ['wupload','fileserve']#,'uploadedto']

# Lista de TODOS los servidores soportados por Filenium
FILENIUM_SERVERS = ['linkto','uploadedto','gigasize','youtube','filepost','hotfile','rapidshare','turbobit','wupload','mediafire','bitshare','depositfiles','oron',
                    'downupload','allmyvideos','novamov','videoweed','movshare','fooget','letitbit','fileserve','shareonline']

# Lista de TODOS los servidores soportados por Real-Debrid
REALDEBRID_SERVERS = ['tenupload','onefichier','twoshared','fourfastfile','fourshared','abc','badongo','bayfiles','bitshare','bulletupload','cbscom','cramit','crocko','cwtv','dailymotion','dateito',
                    'dengee','depositfiles','diglo','easybytez','extabit','fileape','filebox','filedino','filefactory','fileflyer','filejungle','filekeen','filemade','fileover','filepost',
                   'filesend','fileserve','filesmonster','filevelocity','freakshare','free','furk','fyels','gigapeta','gigasize','gigaup','glumbouploads','goldfile','grupload','hitfile',
                   'hotfile','hulkshare','hulu','ifile','jakfile','jumbofiles','justintv','kickload','letitbit','loadto','mediafire','megashare','megashares','mixturevideo','netload',
                   'novamov','przeklej','purevid','putlocker','rapidgator','redtube','rapidshare','rutube','scribd','sendspace','shareonline','shareflare','shragle','slingfile','sockshare',
                   'soundcloud','speedyshare','turbobit','unibytes','uploadboost','uploadc','uploadedto','uploadhere','uploading','uploadking','uploadspace','uploadstation','uptobox',
                   'userporn','videoweed','vidxden','vimeo','vipfile','wattv','wupload','youporn','youtube','yunfile','zippyshare','zshare']

# Lista completa de todos los servidores soportados por pelisalacarta, usada para buscar patrones
ALL_SERVERS = list( set(FREE_SERVERS) | set(FILENIUM_SERVERS) | set(REALDEBRID_SERVERS) )
ALL_SERVERS.sort()

# Función genérica para encontrar vídeos en una página
def find_video_items(item=None, data=None, channel=""):
    logger.info("[launcher.py] findvideos")

    # Descarga la página
    if data is None:
        from core import scrapertools
        data = scrapertools.cache_page(item.url)
        #logger.info(data)
    
    # Busca los enlaces a los videos
    from core.item import Item
    from servers import servertools
    listavideos = servertools.findvideos(data)

    if item is None:
        item = Item()

    itemlist = []
    for video in listavideos:
        scrapedtitle = item.title.strip() + " - " + video[0]
        scrapedurl = video[1]
        server = video[2]
        
        itemlist.append( Item(channel=item.channel, title=scrapedtitle , action="play" , server=server, page=item.page, url=scrapedurl, thumbnail=item.thumbnail, show=item.show , plot=item.plot , folder=False) )

    return itemlist

def findvideos(data):
    logger.info("[servertools.py] findvideos")
    encontrados = set()
    devuelve = []

    # Ejecuta el findvideos en cada servidor
    for serverid in ALL_SERVERS:
        try:
            exec "from servers import "+serverid
            exec "devuelve.extend("+serverid+".find_videos(data))"
        except ImportError:
            logger.info("No existe conector para "+serverid)
        except:
            logger.info("Error en el conector "+serverid)
            import traceback,sys
            from pprint import pprint
            exc_type, exc_value, exc_tb = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_tb)
            for line in lines:
                line_splits = line.split("\n")
                for line_split in line_splits:
                    logger.error(line_split)

    return devuelve

def get_video_urls(server,url):
    '''
    servers_module = __import__("servers."+server)
    server_module = getattr(servers_module,server)
    return server_module.get_video_url( page_url=url)
    '''

    video_urls,puede,motivo = resolve_video_urls_for_playing(server,url)
    return video_urls

def get_channel_module(channel_name):
    channels_module = __import__("channels."+channel_name)
    channel_module = getattr(channels_module,channel_name)
    return channel_module

def get_server_from_url(url):
    encontrado = findvideos(url)
    if len(encontrado)>0:
        devuelve = encontrado[0][2]
    else:
        devuelve = "directo"

    return devuelve

def resolve_video_urls_for_playing(server,url,video_password="",muestra_dialogo=False):

    video_urls = []

    # Si el vídeo es "directo", no hay que buscar más
    if server=="directo" or server=="local":
        if url.startswith("rtmp"):
            video_urls = [[ "%s [%s]" % (url[:4],server) , url ]]
        else:
            video_urls = [[ "%s [%s]" % (url[-4:],server) , url ]]
        return video_urls,True,""

    # Averigua las URL de los vídeos
    else:

        # Carga el conector
        try:
            # Muestra un diálogo de progreso
            if muestra_dialogo:
                import xbmcgui
                progreso = xbmcgui.DialogProgress()
                progreso.create(config.PLUGIN_NAME, "Conectando con " + server)

            exec "from servers import "+server+" as server_connector"

            if muestra_dialogo:
                progreso.update( 25 , "Conectando con "+server)

            # Si tiene una función para ver si el vídeo existe, lo comprueba ahora
            if hasattr(server_connector, 'test_video_exists'):
                puedes,motivo = server_connector.test_video_exists( page_url=url )

                # Si la funcion dice que no existe, fin
                if not puedes:
                    if muestra_dialogo: progreso.close()
                    return video_urls,puedes,motivo

            # Obtiene enlaces free
            if server in FREE_SERVERS:
                video_urls = server_connector.get_video_url( page_url=url , video_password=video_password )
                
                # Si no se encuentran vídeos en modo free, es porque el vídeo no existe
                if len(video_urls)==0:
                    if muestra_dialogo: progreso.close()
                    return video_urls,False,"No se puede encontrar el vídeo en "+server

            # Obtiene enlaces premium si tienes cuenta en el server
            if server in PREMIUM_SERVERS and config.get_setting(server+"premium")=="true":
                video_urls = server_connector.get_video_url( page_url=url , premium=(config.get_setting(server+"premium")=="true") , user=config.get_setting(server+"user") , password=config.get_setting(server+"password"), video_password=video_password )
                
                # Si no se encuentran vídeos en modo premium directo, es porque el vídeo no existe
                if len(video_urls)==0:
                    if muestra_dialogo: progreso.close()
                    return video_urls,False,"No se puede encontrar el vídeo en "+server
    
            # Obtiene enlaces filenium si tienes cuenta
            if server in FILENIUM_SERVERS and config.get_setting("fileniumpremium")=="true":
    
                # Muestra un diálogo de progreso
                if muestra_dialogo:
                    progreso.update( 50 , "Conectando con Filenium")
    
                exec "from servers import filenium as gen_conector"
                
                video_gen = gen_conector.get_video_url( page_url=url , premium=(config.get_setting("fileniumpremium")=="true") , user=config.get_setting("fileniumuser") , password=config.get_setting("fileniumpassword"), video_password=video_password )
                logger.info("[xbmctools.py] filenium url="+video_gen)
                video_urls.append( [ "[filenium]", video_gen ] )

            # Obtiene enlaces realdebrid si tienes cuenta
            if server in REALDEBRID_SERVERS and config.get_setting("realdebridpremium")=="true":
    
                # Muestra un diálogo de progreso
                if muestra_dialogo:
                    progreso.update( 75 , "Conectando con Real-Debrid")

                exec "from servers import realdebrid as gen_conector"
                video_gen = gen_conector.get_video_url( page_url=url , premium=(config.get_setting("realdebridpremium")=="true") , user=config.get_setting("realdebriduser") , password=config.get_setting("realdebridpassword"), video_password=video_password )
                logger.info("[xbmctools.py] realdebrid url="+video_gen)
                if not "REAL-DEBRID" in video_gen:
                    video_urls.append( [ "."+video_gen.rsplit('.',1)[1]+" [realdebrid]", video_gen ] )
                else:
                    if muestra_dialogo: progreso.close()
                    # Si RealDebrid da error pero tienes un enlace válido, no te dice nada
                    if len(video_urls)==0:
                        return video_urls,False,video_gen

                if muestra_dialogo:
                    progreso.update( 100 , "Proceso finalizado")

                # Cierra el diálogo de progreso
                if muestra_dialogo: progreso.close()

            # Llegas hasta aquí y no tienes ningún enlace para ver, así que no vas a poder ver el vídeo
            if len(video_urls)==0:
                # ¿Cual es el motivo?
                
                # 1) No existe -> Ya está controlado
                # 2) No tienes alguna de las cuentas premium compatibles

                # Lista de las cuentas que soportan este servidor
                listapremium = ""
                if server in FILENIUM_SERVERS: listapremium+="Filenium o "
                if server in REALDEBRID_SERVERS: listapremium+="Real-Debrid o "
                if server in PREMIUM_SERVERS: listapremium+=server+" o "
                listapremium = listapremium[:-3]
    
                return video_urls,False,"Para ver un vídeo en "+server+" necesitas<br/>una cuenta en "+listapremium

        except:
            if muestra_dialogo: progreso.close()
            import traceback
            from pprint import pprint
            exc_type, exc_value, exc_tb = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_tb)
            for line in lines:
                line_splits = line.split("\n")
                for line_split in line_splits:
                    logger.error(line_split)

            return video_urls,False,"Se ha producido un error en<br/>el conector con "+server

        try:
            progreso.close()
        except:
            pass

    return video_urls,True,""
