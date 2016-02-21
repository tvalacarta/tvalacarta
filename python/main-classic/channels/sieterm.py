# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para 7rm
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,re
import urllib

from core import logger
from core import scrapertools
from core.item import Item
from core import jsontools

logger.info("tvalacarta.channels.sieterm init")

DEBUG = True
CHANNELNAME = "sieterm"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.sieterm mainlist")

    return categorias(item)

def categorias(item):
    logger.info("tvalacarta.channels.sieterm categorias")

    itemlist = []

    data = scrapertools.cachePage("http://webtv.7tvregiondemurcia.es/")
    data = scrapertools.find_single_match(data,'<ul class="nav center">(.*?)</ul>')
    logger.info("tvalacarta.channels.sieterm data="+data)

    patron  = '<a href="([^"]+)" title="[^"]+">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.strip()

        if title=="Histórico":
            url = "http://www.rtrm.es/servlet/rtrm.servlets.ServletLink2?METHOD=LSTBLOGALACARTA&serv=BlogPortal2&sit=c,6"
            action = "programas_antiguos"
        else:
            url = urlparse.urljoin(item.url,scrapedurl)
            action = "programas"
        
        thumbnail = ""
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=CHANNELNAME, title=title , action=action , url=url, thumbnail=thumbnail, plot=plot ) )
    
    return itemlist

def programas(item, load_all_pages=False):
    logger.info("tvalacarta.channels.sieterm programas")

    itemlist = []

    data = scrapertools.cachePage(item.url)

    '''
    var colecciones = [{"ID":"1204","post_type":"qves_programa_serie","post_title":"Murcia en Vivo","post_subtitle":"","post_content":"Espacio abierto a la retransmisi\u00f3n de actos de car\u00e1cter festivo, institucional y deportivo.","post_name":"murcia-en-vivo","post_date":"2015-07-28 20:13:12","thumbdata":{"width":"320","height":"180","hwstring_small":"height='71' width='128'","file":"2015\/07\/MURCIAVIVO-320x180.jpg","sizes":{"contingut-fondo":{"file":"MURCIAVIVO-1920x1080.jpg","width":"1920","height":"1080"},"contingut-gran-mitjana":{"file":"MURCIAVIVO-640x360.jpg","width":"640","height":"360"},"contingut-mitjana":{"file":"MURCIAVIVO-320x180.jpg","width":"320","height":"180"},"contingut-extra":{"file":"MURCIAVIVO-150x84.jpg","width":"150","height":"84"},"contingut-petita":{"file":"MURCIAVIVO-100x56.jpg","width":"100","height":"56"}},"image_meta":{"aperture":"0","credit":"","camera":"","caption":"","created_timestamp":"0","copyright":"","focal_length":"0","iso":"0","shutter_speed":"0","title":""}},"post_parent_id":"0","post_parent_parent_id":"0","orden":null,"taxonomies":{"menuitem":[{"taxonomy":"menuitem","term_id":"4","name":"Entretenimiento","slug":"entretenimiento","term_order":"0","parent":"0"},{"taxonomy":"menuitem","term_id":"14","name":"Especiales","slug":"especiales","term_order":"0","parent":"0"},{"taxonomy":"menuitem","term_id":"9","name":"Retransmisiones","slug":"retransmisiones","term_order":"0","parent":"0"}]},"properties":[],"menuitem":"retransmisiones","menuitem_title":"Retransmisiones","url":"\/retransmisiones\/murcia-en-vivo\/2015\/carnaval-de-verano-de-mazarron-2015\/","post_content_mini":"Espacio abierto a la retransmisi\u00f3n de actos de...","post_date_mini":"28\/07\/2015"},{"ID":"893","post_type":"qves_programa_serie","post_title":"Hola Verano","post_subtitle":"","post_content":"Programa especial de Verano. Entrevistas y reportajes desde las playas de la Regi\u00f3n de Murcia. Presentado por\u00a0Javier Mart\u00ednez Bastida y Alba Gonz\u00e1lez.","post_name":"hola-verano","post_date":"2015-07-13 14:27:15","thumbdata":{"width":"320","height":"180","hwstring_small":"height='69' width='128'","file":"2015\/07\/Logo-Hola-Verano--320x180.jpg","sizes":{"contingut-fondo":{"file":"Logo-Hola-Verano--1920x1080.jpg","width":"1920","height":"1080"},"contingut-gran-mitjana":{"file":"Logo-Hola-Verano--640x360.jpg","width":"640","height":"360"},"contingut-mitjana":{"file":"Logo-Hola-Verano--320x180.jpg","width":"320","height":"180"},"contingut-extra":{"file":"Logo-Hola-Verano--150x84.jpg","width":"150","height":"84"},"contingut-petita":{"file":"Logo-Hola-Verano--100x56.jpg","width":"100","height":"56"}},"image_meta":{"aperture":"0","credit":"","camera":"","caption":"","created_timestamp":"0","copyright":"","focal_length":"0","iso":"0","shutter_speed":"0","title":""}},"post_parent_id":"0","post_parent_parent_id":"0","orden":null,"taxonomies":{"menuitem":[{"taxonomy":"menuitem","term_id":"4","name":"Entretenimiento","slug":"entretenimiento","term_order":"0","parent":"0"}]},"properties":[],"menuitem":"entretenimiento","menuitem_title":"Entretenimiento","url":"\/entretenimiento\/hola-verano\/2015\/miercoles-2-de-septiembre\/","post_content_mini":"Programa especial de Verano. Entrevistas y...","post_date_mini":"13\/07\/2015"},{"ID":"160","post_type":"qves_programa_serie","post_title":"En su punto con Bar\u00f3","post_subtitle":"","post_content":"Espacio de cocina presentado por Mar\u00eda Dolores Bar\u00f3, una referencia en el mundo de los fogones. Cada d\u00eda una nueva receta y un invitado especial.","post_name":"en-su-punto-con-baro","post_date":"2015-06-22 17:30:29","thumbdata":{"width":"320","height":"180","hwstring_small":"height='96' width='128'","file":"2015\/05\/programas-baro-320x180.jpg","sizes":{"contingut-fondo":{"file":"programas-baro-1920x1080.jpg","width":"1920","height":"1080"},"contingut-gran-mitjana":{"file":"programas-baro-640x360.jpg","width":"640","height":"360"},"contingut-mitjana":{"file":"programas-baro-320x180.jpg","width":"320","height":"180"},"contingut-extra":{"file":"programas-baro-150x84.jpg","width":"150","height":"84"},"contingut-petita":{"file":"programas-baro-100x56.jpg","width":"100","height":"56"}},"image_meta":{"aperture":"0","credit":"","camera":"","caption":"","created_timestamp":"0","copyright":"","focal_length":"0","iso":"0","shutter_speed":"0","title":""}},"post_parent_id":"0","post_parent_parent_id":"0","orden":null,"taxonomies":{"menuitem":[{"taxonomy":"menuitem","term_id":"4","name":"Entretenimiento","slug":"entretenimiento","term_order":"0","parent":"0"}]},"properties":[],"menuitem":"entretenimiento","menuitem_title":"Entretenimiento","url":"\/entretenimiento\/en-su-punto-con-baro\/2015\/jueves-18-de-junio\/","post_content_mini":"Espacio de cocina presentado por Mar\u00eda Dolores...","post_date_mini":"22\/06\/2015"},{"ID":"245","post_type":"qves_programa_serie","post_title":"La 7 Motor","post_subtitle":"","post_content":"Programa del mundo del motor que se emite los s\u00e1bados por la ma\u00f1ana, dirigido por Isidoro Barba, uno de los m\u00e1s experimentados y reputados periodistas del motor a nivel nacional.","post_name":"la-7-motor","post_date":"2015-06-11 10:43:53","thumbdata":{"width":"320","height":"180","hwstring_small":"height='72' width='128'","file":"2015\/06\/motor-320x180.jpg","sizes":{"contingut-fondo":{"file":"motor-1920x1080.jpg","width":"1920","height":"1080"},"contingut-gran-mitjana":{"file":"motor-640x360.jpg","width":"640","height":"360"},"contingut-mitjana":{"file":"motor-320x180.jpg","width":"320","height":"180"},"contingut-extra":{"file":"motor-150x84.jpg","width":"150","height":"84"},"contingut-petita":{"file":"motor-100x56.jpg","width":"100","height":"56"}},"image_meta":{"aperture":"0","credit":"","camera":"","caption":"","created_timestamp":"0","copyright":"","focal_length":"0","iso":"0","shutter_speed":"0","title":""}},"post_parent_id":"0","post_parent_parent_id":"0","orden":null,"taxonomies":{"menuitem":[{"taxonomy":"menuitem","term_id":"4","name":"Entretenimiento","slug":"entretenimiento","term_order":"0","parent":"0"}]},"properties":[],"menuitem":"entretenimiento","menuitem_title":"Entretenimiento","url":"\/entretenimiento\/la-7-motor\/2015\/sabado-25-de-julio\/","post_content_mini":"Programa del mundo del motor que se emite los s...","post_date_mini":"11\/06\/2015"},{"ID":"238","post_type":"qves_programa_serie","post_title":"El Coraz\u00f3n de la Fiesta","post_subtitle":"","post_content":"Programa de reportajes y actualidad, acerca de los festejos t\u00edpicos y las fiestas patronales de los pueblos y ciudades de la Regi\u00f3n de Murcia. Emitido los s\u00e1bados por la tarde-noche.","post_name":"el-corazon-de-la-fiesta","post_date":"2015-06-10 13:04:48","thumbdata":{"width":"320","height":"180","hwstring_small":"height='72' width='128'","file":"2015\/06\/corazonfiesta-320x180.jpg","sizes":{"contingut-fondo":{"file":"corazonfiesta-1920x1080.jpg","width":"1920","height":"1080"},"contingut-gran-mitjana":{"file":"corazonfiesta-640x360.jpg","width":"640","height":"360"},"contingut-mitjana":{"file":"corazonfiesta-320x180.jpg","width":"320","height":"180"},"contingut-extra":{"file":"corazonfiesta-150x84.jpg","width":"150","height":"84"},"contingut-petita":{"file":"corazonfiesta-100x56.jpg","width":"100","height":"56"}},"image_meta":{"aperture":"0","credit":"","camera":"","caption":"","created_timestamp":"0","copyright":"","focal_length":"0","iso":"0","shutter_speed":"0","title":""}},"post_parent_id":"0","post_parent_parent_id":"0","orden":null,"taxonomies":{"menuitem":[{"taxonomy":"menuitem","term_id":"4","name":"Entretenimiento","slug":"entretenimiento","term_order":"0","parent":"0"}]},"properties":[],"menuitem":"entretenimiento","menuitem_title":"Entretenimiento","url":"\/entretenimiento\/el-corazon-de-la-fiesta\/2015\/sabado-29-de-agosto\/","post_content_mini":"Programa de reportajes y actualidad, acerca de...","post_date_mini":"10\/06\/2015"},{"ID":"168","post_type":"qves_programa_serie","post_title":"Yo recuerdo","post_subtitle":"","post_content":"Programa de experiencias y recuerdos de nuestros mayores, en el que tambi\u00e9n participan j\u00f3venes, que conocer\u00e1n c\u00f3mo era la vida de sus abuelos, presentado por Juanma Pi\u00f1ero.","post_name":"yo-recuerdo","post_date":"2015-05-29 17:45:03","thumbdata":{"width":"320","height":"180","hwstring_small":"height='78' width='128'","file":"2015\/05\/programas-yo-recuerdo-320x180.jpg","sizes":{"contingut-fondo":{"file":"programas-yo-recuerdo-1920x1080.jpg","width":"1920","height":"1080"},"contingut-gran-mitjana":{"file":"programas-yo-recuerdo-640x360.jpg","width":"640","height":"360"},"contingut-mitjana":{"file":"programas-yo-recuerdo-320x180.jpg","width":"320","height":"180"},"contingut-extra":{"file":"programas-yo-recuerdo-150x84.jpg","width":"150","height":"84"},"contingut-petita":{"file":"programas-yo-recuerdo-100x56.jpg","width":"100","height":"56"}},"image_meta":{"aperture":"0","credit":"","camera":"","caption":"","created_timestamp":"0","copyright":"","focal_length":"0","iso":"0","shutter_speed":"0","title":""}},"post_parent_id":"0","post_parent_parent_id":"0","orden":null,"taxonomies":{"menuitem":[{"taxonomy":"menuitem","term_id":"4","name":"Entretenimiento","slug":"entretenimiento","term_order":"0","parent":"0"}]},"properties":[],"menuitem":"entretenimiento","menuitem_title":"Entretenimiento","url":"\/entretenimiento\/yo-recuerdo\/2015\/jueves-30-de-julio\/","post_content_mini":"Programa de experiencias y recuerdos de nuestros...","post_date_mini":"29\/05\/2015"},{"ID":"151","post_type":"qves_programa_serie","post_title":"Wasabi","post_subtitle":"","post_content":"Los ni\u00f1os y ni\u00f1as de nuestra Regi\u00f3n son los aut\u00e9nticos protagonistas del programa infantil que est\u00e1 llamado a convertirse en un referente.","post_name":"wasabi","post_date":"2015-05-29 17:24:33","thumbdata":{"width":"320","height":"180","hwstring_small":"height='74' width='128'","file":"2015\/05\/programas-wasabi-320x180.jpg","sizes":{"contingut-fondo":{"file":"programas-wasabi-1920x1080.jpg","width":"1920","height":"1080"},"contingut-gran-mitjana":{"file":"programas-wasabi-640x360.jpg","width":"640","height":"360"},"contingut-mitjana":{"file":"programas-wasabi-320x180.jpg","width":"320","height":"180"},"contingut-extra":{"file":"programas-wasabi-150x84.jpg","width":"150","height":"84"},"contingut-petita":{"file":"programas-wasabi-100x56.jpg","width":"100","height":"56"}},"image_meta":{"aperture":"0","credit":"","camera":"","caption":"","created_timestamp":"0","copyright":"","focal_length":"0","iso":"0","shutter_speed":"0","title":""}},"post_parent_id":"0","post_parent_parent_id":"0","orden":null,"taxonomies":{"menuitem":[{"taxonomy":"menuitem","term_id":"4","name":"Entretenimiento","slug":"entretenimiento","term_order":"0","parent":"0"},{"taxonomy":"menuitem","term_id":"7","name":"Infantil","slug":"infantil","term_order":"0","parent":"0"}]},"properties":[],"menuitem":"infantil","menuitem_title":"Infantil","url":"\/infantil\/wasabi\/2015\/domingo-30-de-agosto\/","post_content_mini":"Los ni\u00f1os y ni\u00f1as de nuestra Regi\u00f3n son los aut...","post_date_mini":"29\/05\/2015"},{"ID":"147","post_type":"qves_programa_serie","post_title":"Gente como t\u00fa","post_subtitle":"","post_content":"El magazine de las tardes de 7 TV se llama Gente como t\u00fa y lo presenta Antonio Hidalgo. Historias cercanas y debates de las cosas que preocupan a la gente.","post_name":"gente-como-tu","post_date":"2015-05-29 17:12:22","thumbdata":{"width":"320","height":"180","hwstring_small":"height='71' width='128'","file":"2015\/05\/gentecomotu-320x180.jpg","sizes":{"contingut-fondo":{"file":"gentecomotu-1920x1080.jpg","width":"1920","height":"1080"},"contingut-gran-mitjana":{"file":"gentecomotu-640x360.jpg","width":"640","height":"360"},"contingut-mitjana":{"file":"gentecomotu-320x180.jpg","width":"320","height":"180"},"contingut-extra":{"file":"gentecomotu-150x84.jpg","width":"150","height":"84"},"contingut-petita":{"file":"gentecomotu-100x56.jpg","width":"100","height":"56"}},"image_meta":{"aperture":"0","credit":"","camera":"","caption":"","created_timestamp":"0","copyright":"","focal_length":"0","iso":"0","shutter_speed":"0","title":""}},"post_parent_id":"0","post_parent_parent_id":"0","orden":null,"taxonomies":{"menuitem":[{"taxonomy":"menuitem","term_id":"4","name":"Entretenimiento","slug":"entretenimiento","term_order":"0","parent":"0"}]},"properties":[],"menuitem":"entretenimiento","menuitem_title":"Entretenimiento","url":"\/entretenimiento\/gente-como-tu\/2015\/viernes-31-de-julio\/","post_content_mini":"El magazine de las tardes de 7 TV se llama Gente...","post_date_mini":"29\/05\/2015"},{"ID":"143","post_type":"qves_programa_serie","post_title":"Murcia Conecta","post_subtitle":"","post_content":"Mar\u00eda Pina es la presentadora de este espacio diario que conecta con los diferentes pueblos y comarcas de la Regi\u00f3n con reportajes y conexiones en directo.","post_name":"murcia-conecta","post_date":"2015-05-29 17:01:31","thumbdata":{"width":"320","height":"180","hwstring_small":"height='71' width='128'","file":"2015\/05\/murcia-conecta-320x180.jpg","sizes":{"contingut-fondo":{"file":"murcia-conecta-1920x1080.jpg","width":"1920","height":"1080"},"contingut-gran-mitjana":{"file":"murcia-conecta-640x360.jpg","width":"640","height":"360"},"contingut-mitjana":{"file":"murcia-conecta-320x180.jpg","width":"320","height":"180"},"contingut-extra":{"file":"murcia-conecta-150x84.jpg","width":"150","height":"84"},"contingut-petita":{"file":"murcia-conecta-100x56.jpg","width":"100","height":"56"}},"image_meta":{"aperture":"0","credit":"","camera":"","caption":"","created_timestamp":"0","copyright":"","focal_length":"0","iso":"0","shutter_speed":"0","title":""}},"post_parent_id":"0","post_parent_parent_id":"0","orden":null,"taxonomies":{"menuitem":[{"taxonomy":"menuitem","term_id":"4","name":"Entretenimiento","slug":"entretenimiento","term_order":"0","parent":"0"},{"taxonomy":"menuitem","term_id":"5","name":"Informativos","slug":"informativos","term_order":"0","parent":"0"}]},"properties":[],"menuitem":"informativos","menuitem_title":"Informativos","url":"\/informativos\/murcia-conecta\/2015\/miercoles-2-de-septiembre\/","post_content_mini":"Mar\u00eda Pina es la presentadora de este espacio...","post_date_mini":"29\/05\/2015"}];
    '''

    json_body = scrapertools.find_single_match(data,'var colecciones = (.*?\}\])\;')
    logger.info("tvalacarta.channels.sieterm json_body="+json_body)
    json_object = jsontools.load_json(json_body)
    logger.info("tvalacarta.channels.sieterm json_object="+repr(json_object))

    for entry in json_object:
        logger.info("tvalacarta.channels.sieterm entry="+repr(entry))

        title = entry["post_title"]
        plot = entry["post_content"]
        thumbnail = "http://statics.7tvregiondemurcia.es/uploads/"+entry["thumbdata"]["file"]
        url = "http://webtv.7tvregiondemurcia.es/temporadasbrowser/getCapitulos/"+entry["ID"]+"/1/1/"
        fanart = thumbnail
        page = urlparse.urljoin( item.url , entry["url"] )

        # Añade al listado de XBMC
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="temporadas" , url=url, thumbnail=thumbnail, fanart=fanart, category=item.title, plot=plot, show=title, page=page, viewmode="movie_with_plot" ) )
    
    return itemlist

def temporadas(item, load_all_pages=False):
    logger.info("tvalacarta.channels.sieterm temporadas")

    itemlist = []

    json_body = scrapertools.cachePage(item.url)
    json_object = jsontools.load_json(json_body)
    logger.info("tvalacarta.channels.sieterm json_object="+repr(json_object))

    for entry in json_object["episodes"]:
        logger.info("tvalacarta.channels.sieterm entry="+repr(entry))

        title = "Temporada "+entry["post_title"]
        plot = entry["post_content"]
        thumbnail = item.thumbnail
        url = "http://webtv.7tvregiondemurcia.es/temporadasbrowser/getCapitulos/"+entry["ID"]+"/1/1/"
        fanart = thumbnail

        # Añade al listado de XBMC
        temporadaitem = Item(channel=CHANNELNAME, title=title , action="videos" , url=url, thumbnail=thumbnail, fanart=fanart, plot=plot, category=item.category, show=item.show )
        itemlist.extend( videos(temporadaitem,load_all_pages) )
    
    return itemlist

def videos(item, load_all_pages=False):
    logger.info("tvalacarta.channels.sieterm videos")

    itemlist = []

    json_body = scrapertools.cachePage(item.url)
    json_object = jsontools.load_json(json_body)
    logger.info("tvalacarta.channels.sieterm json_object="+repr(json_object))

    for entry in json_object["episodes"]:
        logger.info("tvalacarta.channels.sieterm entry="+repr(entry))

        title = entry["post_title"]
        plot = entry["post_content"]
        thumbnail = entry["image"]
        url = urlparse.urljoin( item.url , entry["url"] )
        fanart = thumbnail

        # Trata de sacar la fecha de emisión del título
        aired_date = entry["post_date"][0:10]

        # Añade al listado de XBMC
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="play", server="sieterm" , url=url, thumbnail=thumbnail, fanart=fanart, plot=plot, show=item.show, aired_date=aired_date, viewmode="movie_with_plot", folder=False ) )
    
    if json_object["hasNext"]:

        # Extrae la página de la URL
        trozos = item.url.split("/")
        current_page = trozos[-2]

        # La aumenta
        next_page = int(current_page)+1
        trozos[-2] = str(next_page)

        # Y recompone la URL
        next_page_url = "/".join(trozos)
        next_page_item = Item(channel=CHANNELNAME, title=">> Página siguiente" , action="videos" , url=next_page_url, thumbnail=thumbnail, fanart=fanart, show=item.show, viewmode="movie_with_plot" )

        if load_all_pages:
            itemlist.extend(videos(next_page_item, load_all_pages))
        else:
            itemlist.append( next_page_item )

    return itemlist

def programas_antiguos(item, load_all_pages=False):
    logger.info("tvalacarta.channels.sieterm programas_antiguos load_all_pages=="+repr(load_all_pages))

    itemlist = []

    data = scrapertools.cachePage(item.url)
    
    # Extrae las entradas (carpetas)
    patron  = '<dt class="alacarta-video">[^<]+'
    patron += '<a href="([^"]+)">([^<]+)</a>[^<]+'
    patron += '</dt>[^<]+'
    patron += '<dd style="height:100%;overflow:hidden;">[^<]+'
    patron += '<a[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '</a>([^<]+)</dd>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    itemlist = []
    for match in matches:
        # Atributos del vídeo
        scrapedtitle = unicode( match[1].strip() , "iso-8859-1" , errors="ignore").encode("utf-8")
        scrapedurl = urlparse.urljoin(item.url,match[0]).replace("&amp;","&")
        scrapedthumbnail = urlparse.urljoin(item.url,match[2]).replace("&amp;","&")
        scrapedplot = unicode( match[3].strip() , "iso-8859-1" , errors="ignore").encode("utf-8")
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot , show=scrapedtitle , viewmode="movie_with_plot" ) )

    # Busca la página siguiente
    next_page_url = scrapertools.find_single_match(data,'<a class="list-siguientes" href="([^"]+)" title="Ver siguientes a la cartas">Siguiente</a>')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        next_page_item = Item(channel=CHANNELNAME, title=">> Página siguiente" , action="programas_antiguos" , url=next_page_url , folder=True)

        if load_all_pages:
            itemlist.extend(programas_antiguos(next_page_item,load_all_pages=True))
        else:
            itemlist.append( next_page_item )

    return itemlist

def episodios(item, load_all_pages=False):
    logger.info("tvalacarta.channels.sieterm episodios")

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    #logger.info(data)

    # Extrae los vídeos
    '''
    <dt class="alacarta-video"><a href="http://..." title="...">Murcianos por el mundo: Cracovia</a> · 12/05/2010 · (5411 veces visto)</dt>
    <dd style="height:100%; overflow:hidden">
    <a href="http://www.7rm.es/servlet/rtrm.servlets.ServletLink2?METHOD=DETALLEALACARTA&amp;sit=c,6,ofs,10&amp;serv=BlogPortal2&amp;orden=1&amp;idCarta=40&amp;mId=4182&amp;autostart=TV" title="Ver v&iacute;deo">
    <img src="http://mediateca.regmurcia.com/MediatecaCRM/ServletLink?METHOD=MEDIATECA&amp;accion=imagen&amp;id=4182" alt="Murcianos por el mundo: Cracovia" title="Murcianos por el mundo: Cracovia" style="width:95px" />
    </a>
    Esta semana nos desplazamos al sur de Polonia, a Cracovia y Wroclaw, para conocer cómo viven seis murcianos en una de las ciudades más importantes de Polonia y Patrimonio de la Humanidad.
    <a href="http://ficheros.7rm.es:3025/Video/4/1/4182_BAJA.mp4">
    <img src="/images/bajarArchivo.gif" alt="Descargar Archivo" title="Descargar Archivo" style="margin:0;padding:0 5px 0 0;vertical-align:middle;border:none" />
    </a>
    </dd>
    '''
  
    '''
    <dt class="alacarta-video"><a href="http://www.7rm.es/servlet/rtrm.servlets.ServletLink2?METHOD=DETALLEALACARTA&amp;sit=c,6,ofs,0&amp;serv=BlogPortal2&amp;orden=2&amp;idCarta=36&amp;mId=3214&amp;autostart=TV" title="Ver v&iacute;deo">De la tierra al mar</a> · 22/12/2009 · (1072 veces visto)</dt>
    <dd style="height:100%; overflow:hidden">
    <a href="http://www.7rm.es/servlet/rtrm.servlets.ServletLink2?METHOD=DETALLEALACARTA&amp;sit=c,6,ofs,0&amp;serv=BlogPortal2&amp;orden=2&amp;idCarta=36&amp;mId=3214&amp;autostart=TV" title="Ver v&iacute;deo">
    <img src="http://mediateca.regmurcia.com/MediatecaCRM/ServletLink?METHOD=MEDIATECA&amp;accion=imagen&amp;id=3214" alt="De la tierra al mar" title="De la tierra al mar" style="width:95px" />
    </a>
    En este programa conocemos a Plácido, joven agricultor que nos mostrará la mala situación en que se encuentra el sector, informamos de la campaña 'Dale vida a tu árbol', asistimos a la presentación del libro 'Gestión ambiental. Guía fácil para empresas y profesionales', y nos hacemos eco del malestar de nuestros agricultores con la nueva normativa europea en materia de fitosanitarios, que entrará en vigor en junio de 2011.
    <a href="http://ficheros.7rm.es:3025/Video/3/2/3214_BAJA.mp4">
    <img src="/images/bajarArchivo.gif" alt="Descargar Archivo" title="Descargar Archivo" style="margin:0;padding:0 5px 0 0;vertical-align:middle;border:none" />
    </a>
    </dd>
    '''
    patron  = '<dt class="alacarta-video"><a href="([^"]+)" title="[^"]+">([^<]+)</a>.*?([0-9\/]+).*?</dt>[^<]+'
    patron += '<dd style="[^<]+">[^<]+'
    patron += '<a href="[^"]+" title="[^"]+">[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '</a>([^<]+)<a href="([^"]+)">'
    matches = re.compile(patron,re.DOTALL).findall(data)
    #scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        # Atributos del vídeo
        scrapedtitle = unicode( match[1].strip()+" ("+match[2]+")" , "iso-8859-1" , errors="ignore").encode("utf-8")
        scrapedurl = urlparse.urljoin(item.url,match[5]).replace("&amp;","&")
        scrapedthumbnail = urlparse.urljoin(item.url,match[3]).replace("&amp;","&")
        scrapedplot = unicode( match[4].strip()  , "iso-8859-1" , errors="ignore").encode("utf-8")
        scrapedpage = urlparse.urljoin(item.url,match[0]).replace("&amp;","&")
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], page=["+scrapedpage+"], thumbnail=["+scrapedthumbnail+"]")

        # Trata de sacar la fecha de emisión del título
        aired_date = scrapertools.parse_date(scrapedtitle)
        #logger.info("aired_date="+aired_date)

        # Añade al listado de XBMC
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , server="sieterm" , url=scrapedpage, thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot , show = item.show , page=scrapedpage, viewmode="movie_with_plot", aired_date=aired_date, folder=False) )

    # Busca la página siguiente
    next_page_url = scrapertools.find_single_match(data,'<a class="list-siguientes" href="([^"]+)" title="Ver siguientes archivos">')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        next_page_item = Item(channel=CHANNELNAME, title=">> Página siguiente" , action="episodios" , url=next_page_url , show=item.show, folder=True)

        if load_all_pages:
            itemlist.extend(episodios(next_page_item,load_all_pages))
        else:
            itemlist.append( next_page_item )

    return itemlist

def detalle_episodio(item):

    #data = scrapertools.cache_page(item.url)

    item.geolocked = "0"

    try:
        from servers import sieterm as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[-1][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def play(item):

    item.server="sieterm";
    itemlist = [item]

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    menuitem = mainlist(Item())[0]
    # El canal tiene estructura programas -> episodios -> play
    programas_itemlist = programas(menuitem)
    if len(programas_itemlist)==0:
        return False

    print "Episodios de "+programas_itemlist[1].tostring()
    episodios_itemlist = episodios(programas_itemlist[1])
    if len(episodios_itemlist)==0:
        return False

    return bien
