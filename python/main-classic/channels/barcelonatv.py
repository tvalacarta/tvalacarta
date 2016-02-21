# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para barcelonatv
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import logger
from core import scrapertools
from core.item import Item

logger.info("[barcelonatv.py] init")

DEBUG = False
CHANNELNAME = "barcelonatv"

def isGeneric():
    return True

def mainlist(item):
    logger.info("[barcelonatv.py] mainlist")
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page( "http://www.btv.cat/wp-admin/admin-ajax.php" , post="action=fm_get_all_channels")
    patron = '\{"label"\:"([^"]+)","value"\:(\d+)\}'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for title,id in matches:
        scrapedtitle = title
        scrapedurl = id
        scrapedthumbnail = ""
        scrapedplot = ""

        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , folder=True) )

    return itemlist

def episodios(item):
    logger.info("[barcelonatv.py] episodios")
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page("http://www.btv.cat/alacarta",post="prog_id="+item.url)
    '''
    <div class="all_box act" id="all_box_14437">
    <div class="pl_th"><a href="http://www.btv.cat/alacarta/telemonegal-1/14437" title="Veure vídeo" id="14437" rel="alacarta_playlist" ><img src="http://api.barcelonatv2.webtv.flumotion.com/videos/14437/thumbnail.jpg?w=1bc99045" width="80" height="50"></a></div>
    <div class="pl_txt">
    <span class="pl_tit"><a title="Veure vídeo" href="http://www.btv.cat/alacarta/telemonegal-1/14437" id="14437" rel="alacarta_playlist" >Telemonegal: JOSEF AJRAM</a></span>
    <span class="pl_sub">14.02.2012</span>
    </div><div class="pl_dsp" rel="14437"><div><span class="oculto">Desplegar</span></div></div><div id="pl_inf_14437" class="pl_inf"><p>Aquesta setmana tenim a plató una criatura molt peculiar que ha anat guanyant popularitat a mida que la crisi també anava in crescendo: Josef Ajram. Aquest barceloní de 33 anys, de pare siri i mare catalana, és una peculiar barreja d'esportista "ultraman" i broker borsari que ha fet dels seus tatuatges i pírcings un segell propi.</p></div>
    </div>
    
    <div class="all_box " id="all_box_13850">
    <div class="pl_th"><a href="http://www.btv.cat/alacarta/telemonegal-1/13850" title="Veure vídeo" id="13850" rel="alacarta_playlist" ><img src="http://api.barcelonatv2.webtv.flumotion.com/videos/13850/thumbnail.jpg?w=c4b93e48" width="80" height="50"></a></div>
    <div class="pl_txt">
    <span class="pl_tit"><a title="Veure vídeo" href="http://www.btv.cat/alacarta/telemonegal-1/13850" id="13850" rel="alacarta_playlist" >Telemonegal: TINET RUBIRA</a></span>
    <span class="pl_sub">31.01.2012</span>
    </div><div class="pl_dsp" rel="13850"><div><span class="oculto">Desplegar</span></div></div><div id="pl_inf_13850" class="pl_inf"><p>Aquest dimarts tenim l'honor de tenir a les nostres pantalles al gran director, productor, guionista, realitzador i quantes coses vulgueu Tinet Rubira, creador de formats como ara Operación Triunfo o La granja de los famosos. Una ment televisivament prodigiosa que ens pot explicar moltes coses del mitjà.</p></div>
    </div>
    '''
    patron  = '<div class="all_box[^"]+" id="all_box[^<]+'
    patron += '<div class="pl_th"><a href="([^"]+)" title="Veure[^<]+<img src="([^"]+)"[^<]+</a></div>[^<]+'
    patron += '<div class="pl_txt">[^<]+'
    patron += '<span class="pl_tit"><a title="Veure[^>]+>([^<]+)</a></span>[^<]+'
    patron += '<span class="pl_sub">([^<]+)</span>[^<]+'
    patron += '</div><div class="pl_dsp".*?<div id="pl_inf[^"]+" class="pl_inf">(.*?)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for url,thumbnail,titulo,fecha,argumento in matches:
        scrapedtitle = titulo+" "+fecha
        scrapedurl = url
        scrapedthumbnail = thumbnail
        scrapedplot = argumento
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , folder=False) )

    # Extrae el enlace a la siguiente página
    #mostrar_llista_videos('10', '8', '14437','8')
    #http://www.btv.cat/wp-content/themes/btv_cat_2011/ajax.php?num_videos=10&id_canal=8&id_video=14437&id_player=8&exclude_video_id=14437&page_playlist=2&action=mesVideos
    patron  = "mostrar_llista_videos\('(\d+)', '(\d+)', '(\d+)','(\d+)'\)"
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for num_videos,id_canal,id_video,id_player in matches:
        pagina = item.extra
        if pagina=="":
            pagina="2"
        else:
            pagina = str(int(pagina)+1)
        scrapedtitle = "!Página siguiente >>"
        scrapedurl = "http://www.btv.cat/wp-content/themes/btv_cat_2011/ajax.php?num_videos=%s&id_canal=%s&id_video=%s&id_player=%s&exclude_video_id=%s&page_playlist=%s&action=mesVideos" % (num_videos,id_canal,id_video,id_player,id_video,pagina)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra=pagina, folder=True) )

    return itemlist

def play(item):
    logger.info("[barcelonatv.py] play")

    # Averigua la URL y la descripcion
    # http://www.btv.cat/alacarta/telemonegal-1/13020/
    # <input type="hidden" name="auth_signature" id="auth_signature" value="api_key=VQX6aBAx6q3SZ2AM&api_nonce=54268651&api_referrer=www.btv.cat&api_timestamp=1329779310&api_signature=fad76d821e2387f59c745aa1b2595e0ea3029287">
    # http://api.barcelonatv2.webtv.flumotion.com/video/13020/streams?api%5Fnonce=08803205927833915&api%5Fsignature=b09b0dd477c8ca759eed0c30b4ec63ca1b752319&api%5Freferrer=www%2Ebtv%2Ecat&api%5Fkey=VQX6aBAx6q3SZ2AM&api%5Ftimestamp=1329779347&session=50D3E703E42D131775C69D0690D65BCC
    '''
    [
    {
    "format": "mp4", 
    "url": "http://ondemand.barcelonatv.ondemand.flumotion.com/barcelonatv/ondemand/video/mp4/high/76-358.mp4?token=cac943525f6a5d019dbbde3e7354147c4f42d2584f442414", 
    "quality": "high", 
    "seekparam": "start", 
    "expire": 86400, 
    "bitrate": 1200
    }, 
    {
    "format": "mp4", 
    "url": "http://ondemand.barcelonatv.ondemand.flumotion.com/barcelonatv/ondemand/video/mp4/low/76-358.mp4?token=ed37105f1c4a15f19b88bdced12685004f42d2584f442414", 
    "quality": "low", 
    "seekparam": "start", 
    "expire": 86400, 
    "bitrate": 400
    }, 
    {
    "format": "mp4", 
    "url": "http://ondemand.barcelonatv.ondemand.flumotion.com/barcelonatv/ondemand/video/mp4/mobile/76-358.mp4?token=0916c0dd9e28bb8be21ee223a2ec11884f42d2584f442414", 
    "quality": "mobile", 
    "seekparam": "start", 
    "expire": 86400, 
    "bitrate": 350
    }, 
    {
    "format": "mp4", 
    "url": "http://ondemand.barcelonatv.ondemand.flumotion.com/barcelonatv/ondemand/video/mp4/mini/76-358.mp4?token=4240a555ffaa81aee956f249cfc10bb14f42d2584f442414", 
    "quality": "mini", 
    "seekparam": "start", 
    "expire": 86400, 
    "bitrate": 500
    }
    ]
    '''
    # http://ondemand.barcelonatv.ondemand.flumotion.com/barcelonatv/ondemand/video/mp4/low/76-358.mp4?token=ed37105f1c4a15f19b88bdced12685004f42d2584f442414
    data = scrapertools.cachePage(item.url)
    patron = '<PARAM NAME="url" VALUE="([^"]+)">'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    try:
        url = matches[0]
    except:
        url = ""

    patron = 'so.addVariable\("sinopsis", "([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    try:
        scrapedplot = matches[0]
    except:
        scrapedplot = ""

    # Descarga el .ASX
    data = scrapertools.cachePage(url)
    patron = 'href="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    
    try:
        url = matches[len(matches)-1]
    except:
        url = ""
    
    logger.info("[barcelonatv.py] scrapedplot="+scrapedplot)

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title=item.title , action="play" , url=url, thumbnail=item.thumbnail , plot=scrapedplot , server = "directo" , folder=False) )

    return itemlist