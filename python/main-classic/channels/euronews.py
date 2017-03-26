# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal EURONEWS
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import logger
from core import scrapertools
from core.item import Item
from core import jsontools

DEBUG = False
CHANNELNAME = "euronews"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.euronews mainlist")

    itemlist = []

    data = scrapertools.cache_page("http://www.euronews.com/programs")
    data = scrapertools.find_single_match(data,'<ul class="menu vertical">(.*?)</div[^<]+</li[^<]+</ul>')
    '''
    <option  dir="ltr" style="text-align:left" lang="en" value="http://www.euronews.com/">English</option>
    <option class="alt"  dir="ltr" style="text-align:left" lang="fr" value="http://fr.euronews.com/">Français</option>
    <option  dir="ltr" style="text-align:left" lang="de" value="http://de.euronews.com/">Deutsch</option>
    <option class="alt"  dir="ltr" style="text-align:left" lang="it" value="http://it.euronews.com/">Italiano</option>
    '''
    patron = '<a href="([^"]+)"[^>]+>([^<]+)</a>'
    matches = re.findall(patron,data,re.DOTALL)
    for url,idioma in matches:
        itemlist.append( Item(channel=CHANNELNAME, title=idioma, action="programas", view="programs", url=url) )

    return itemlist

def programas(item):
    logger.info("tvalacarta.euronews programas")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    '''
    <div class="letter-programs">
    <a class="program" href="http://es.euronews.com/programas/futuris">
    <div class="program-img column medium-3 large-3 xlarge-3 small-5">
    <img src="http://static.euronews.com/articles/programs/320x240_futuris.jpg" alt="futuris" onerror="this.onerror=null;this.src='/images/fallback-320.jpg';" />
    </div>
    <div class="program-txt column medium-7 large-7 x-large-7 small-7">
    <h3>Futuris</h3>
    <p>últimas noticias sobre los principales proyectos científicos y tecnológicos en Europa, descubrir los secretos de la investigación, la ciencia y la tecnología, todo ello en vídeo a la carta</p>
    </div>
    '''
    patron  = '<div class="letter-programs"[^<]+'
    patron += '<a class="program" href="([^"]+)"[^<]+'
    patron += '<div[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '</div[^<]+'
    patron += '<div[^<]+'
    patron += '<h3>([^<]+)</h3[^<]+'
    patron += '<p>([^<]+)</p'

    matches = re.findall(patron,data,re.DOTALL)
    
    for url,thumbnail,titulo,plot in matches:
        itemlist.append( Item(channel=CHANNELNAME, title=titulo, action="videos", url=urlparse.urljoin(item.url,url), thumbnail=thumbnail, plot=plot, view="videos", fanart=thumbnail, show=titulo, folder=True) )

    return itemlist

def videos(item):
    logger.info("tvalacarta.euronews videos")
    itemlist = []

    #http://es.euronews.com/api/program/futuris
    #http://es.euronews.com/programas/futuris
    data = scrapertools.cache_page(item.url.replace("/programas/","/api/program/"))

    json_objects = jsontools.load_json(data)

    for json_object in json_objects:
        try:
            title = json_object["title"]
            url = json_object["canonical"]
            thumbnail = json_object["images"][0]["url"].replace("{{w}}","960").replace("{{h}}","540")
            plot = json_object["plainText"]

            import datetime
            aired_date = datetime.datetime.fromtimestamp( json_object["publishedAt"] ).strftime('%Y-%m-%d %H:%M:%S')
            logger.info("aired_date="+repr(aired_date))

            # Intenta acceder al vídeo, si no tiene deja que la excepción salte y el vídeo no se añada
            video_element = json_object["videos"][0]

            try:
                duration = json_object["videos"][0]["duration"]
                logger.info("duration="+duration)
                duration = scrapertools.parse_duration_secs( str(int(duration)/1000) )
                logger.info("duration="+duration)
            except:
                duration = ""

            itemlist.append( Item(channel=CHANNELNAME, action="play", server="euronews", title=title, url=url, thumbnail=thumbnail, plot=plot, aired_date=aired_date, duration=duration, show=item.show, folder=False) )
        except:
            logger.info("Error al cargar "+title)

    return itemlist

def detalle_episodio(item):

    # Ahora saca de PakaPaka la URL
    data = scrapertools.cache_page(item.url)

    item.geolocked = "0"    
    try:
        from servers import euronews as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    idiomas_items = mainlist(Item())
    categorias_items = categorias(idiomas_items[0])

    # Comprueba que salgan programas
    for categoria_item in categorias_items:
        if categoria_item.action=="programas":
            programas_items = programas(categoria_item)
            if len(programas_items)==0:
                print "No hay programas"
                return False

    # Busca una lista de videos no vacia
    for categoria_item in categorias_items:
        if categoria_item.action=="videos":
            videos_items = videos(categoria_item)
            if len(videos_items)>0:
                return True

    print "No hay videos en ninguna categoria"

    return False
