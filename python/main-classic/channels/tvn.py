# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para TVN (Chile)
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import logger
from core import config
from core import scrapertools
from core.item import Item

DEBUG = True
CHANNELNAME = "tvn"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.tvn mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Programas"  , action="programas" , url="http://www.tvn.cl/programas", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Teleseries" , action="programas" , url="http://www.tvn.cl/teleseries", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Cultura"    , action="programas" , url="http://www.tvn.cl/cultura", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Especiales" , action="programas" , url="http://www.tvn.cl/especiales", folder=True) )

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.tvn programas")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    patron = '<ul class="nav_videos_destacados">(.*?)</ul>'
    bloques = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(bloques)

    for bloque in bloques:

        '''
        <li id='comcont11808009_1'>
        <a href="http://www.tvn.cl/programas/kunga/" >
        <img alt="Kunga" src="http://www.tvn.cl/incoming/afiche-kungapng-1852994/ALTERNATES/w620h450/Afiche-Kunga.png" />
        <div class="nav_videos_destacados_txt">
        <span>Sábado 22:30 horas</span>
        <h3>Kunga</h3>
        <p>Actitud Animal</p>
        '''
        '''
        <li id='comcont11807952_6'>
        <a href="http://www.tvn.cl/programas/mientrastanto/" >
        <img alt="Mientras Tanto" src="http://www.tvn.cl/incoming/afiche-mientrastantopng-1853001/ALTERNATES/w620h450/Afiche-MientrasTanto.png" />
        <div class="nav_videos_destacados_txt">
        <span></span>
        <h3>Mientras Tanto</h3>
        <p>#MientrasTantoTVN</p>
        </div>
        </a>
        </li>
        '''

        patron  = '<li[^<]+'
        patron += '<a href="([^"]+)"[^<]+'
        patron += '<img alt="[^"]+" src="([^"]+)"[^<]+'
        patron += '<div class="nav_videos_destacados_txt"[^<]+'
        patron += '<span>[^<]*</span[^<]+'
        patron += '<h3>([^<]+)</h3[^<]+'
        patron += '<p>([^<]*)</p>'
        matches = re.compile(patron,re.DOTALL).findall(bloque)
        if DEBUG: scrapertools.printMatches(matches)

        for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedplot in matches:
            title = scrapedtitle.strip()
            thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
            plot = scrapedplot
            url = urlparse.urljoin(item.url,scrapedurl)
            if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
            itemlist.append( Item( channel=item.channel , title=title , action="episodios" , url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=True ) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.tvn episodios")
    itemlist=[]

    episode_url = urlparse.urljoin(item.url,"capitulos")
    data = scrapertools.cache_page(episode_url)

    itemlist = parse_itemlist_teleserie(item,data)

    if len(itemlist)==0:
        episode_url = item.url
        data = scrapertools.cache_page(episode_url)

        itemlist = parse_itemlist_teleserie(item,data)

    return itemlist

def parse_itemlist_teleserie(item,data):
    logger.info("tvalacarta.channels.tvn parse_itemlist_teleserie")

    # Ultimo capitulo
    '''
    <article>
    <a href="http://www.tvn.cl/teleseries/moises/capitulos/moises-y-los-10-mandamientos-capitulo-49-1927494">
    <img src="http://www.tvn.cl/incoming/moises49jpg-1927492/ALTERNATES/w620h450/moises49.jpg" alt="Moisés llegó a un lugar seguro - Parte 1"/>
    <div>
    <span>Capítulo 49 - Miércoles 10 de Febrero</span>
    <h3>Moisés llegó a un lugar seguro - Parte 1</h3>
    <p>Tras un extenuante viaje por el desierto, Moisés logró sobrevivir al calor y llegó hasta un oasis do...</p>
    </div>
    </a>
    </article>
    '''
    patron  = '<article[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '<div[^<]+'
    patron += '<span>([^<]*)</span[^<]+'
    patron += '<h3>([^<]*)</h3[^<]+'
    patron += '<p>([^<]*)</p'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    primer_episodio = []
    for scrapedurl,scrapedthumbnail,scrapedtitle,subtitle,scrapedplot in matches:
        title = scrapedtitle.strip()+" - "+subtitle.strip()
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = scrapedplot
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        primer_episodio.append( Item( channel=item.channel , title=title , action="play" , server="tvn", url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=False ) )

    # Ultimo capitulo, player embebido

    '''
    <article>
    <a name="video"></a>
    <a id='playerFeaturedVideo1361789' class='player'></a>
    <div>
    <span>Viernes 12 de febrero</span>
    <h3>Tristán se enteró de la verdad - parte 1</h3>
    <p>Tristán descubrió a Jacinta cuando le decía a Carmen que ella siempre sería Aurora y no pudo creer por qué no se había dado cuenta antes. Lo único que alcanzó a decirle a la farsante, antes de que huyera, fue que nunca más le volviera a decir padre. </p>
    </div>
    </article>
    '''
    patron  = '<article[^<]+'
    patron += '<a name="video"></a[^<]+'
    patron += "<a id='playerFeaturedVideo[^<]+</a[^<]+"
    patron += '<div[^<]+'
    patron += '<span>([^<]*)</span[^<]+'
    patron += '<h3>([^<]*)</h3[^<]+'
    patron += '<p>([^<]*)</p'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedtitle,subtitle,scrapedplot in matches:
        title = scrapedtitle.strip()+" - "+subtitle.strip()
        thumbnail = ""
        plot = scrapedplot
        url = item.url
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        primer_episodio.append( Item( channel=item.channel , title=title , action="play" , server="tvn", url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=False ) )

    # Resto
    '''
    <li id='comcont11883996_145'>
    <a href="http://www.tvn.cl/teleseries/moises/capitulos/capitulo-1-moises-y-los-10-mandamientos-1884164" >
    <img alt="La cruel condena a los hebreos - Parte 1" src="http://www.tvn.cl/incoming/moises-capitulo-1jpg-1884163/ALTERNATES/w620h450/moises-capitulo-1.jpg" />
    <div class="nav_videos_destacados_txt">
    <span>Capítulo 1 - Lunes 28 de diciembre</span>
    <h3>La cruel condena a los hebreos - Parte 1</h3>
    <p>Jocabed junto a su esposo Aarón hacen todo lo posible para salvar a su hijo recién nacido de las gar...</p>
    </div>
    '''

    '''
    <li id='comcont11207754_1'>
    <a href="http://www.tvn.cl/teleseries/volveraamar/capitulos/el-hijo-de-maria-paz-fue-dado-en-adopcion-1511310" >
    <img alt="El hijo de María Paz fue dado en adopción" src="http://www.tvn.cl/incoming/article1511312.ece/ALTERNATES/w460h260/volver-a-amar-cap139.jpg" />
    <div class="nav_videos_destacados_txt">
    <span>Capítulo 139 - Viernes 28 noviembre</span>
    <h3>El hijo de María Paz fue dado en adopción</h3>
    <p>Cada día más fuera de control, Franco arrancó de la clínica con el hijo de María Paz en los brazos. Luego lo entregó a una mujer que pretende darle un destino en el extranjero al niño. Franco disfruta de cada momento desgracia que vive su hermano junto a su ex mujer. </p>
    </div> </a>
    '''

    '''
    <li id='comcont11800540_2'>
    <a href="http://www.tvn.cl/programas/meloyastorga/dan-cruishank-placer-1915528" >
    <img alt="La arquitectura del placer" src="http://www.tvn.cl/incoming/arquitecturaplacerjpg-1918486/ALTERNATES/w620h450/ArquitecturaPlacer.jpg" />
    <div class="nav_videos_destacados_txt">
    <span>Dan Cruishank</span>
    <h3>La arquitectura del placer</h3>
    <p>Hedonismo, placer y grandes gustos en la arquitectura.</p>
    </div>
    '''

    patron  = '<li[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img alt="[^"]+" src="([^"]+)".*?'
    patron += '<div class="nav_videos_destacados[^<]+'
    patron += '<span>([^<]*)</span[^<]+'
    patron += '<h3>([^<]*)</h3[^<]+'
    patron += '<p>([^<]*)</p>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    resto_episodios = []
    for scrapedurl,scrapedthumbnail,scrapedtitle,subtitle,scrapedplot in matches:
        title = scrapedtitle.strip()+" - "+subtitle.strip()
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = scrapedplot
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        resto_episodios.append( Item( channel=item.channel , title=title , action="play" , server="tvn", url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=False ) )

    return primer_episodio + resto_episodios

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    
    # El canal tiene estructura
    items_mainlist = mainlist(Item())
    items_programas = []

    # Todas las opciones del menu tienen que tener algo
    for item_mainlist in items_mainlist:
        exec "itemlist="+item_mainlist.action+"(item_mainlist)"
    
        if len(itemlist)==0:
            print "La sección '"+item_mainlist.title+"' no devuelve nada"
            return False

        items_programas = itemlist

    # Ahora recorre los programas hasta encontrar vídeos en alguno
    for item_programa in items_programas:
        print "Verificando "+item_programa.title
        items_episodios = episodios(item_programa)

        if len(items_episodios)>0:
            return True

    print "No hay videos en ningún programa"
    return False
