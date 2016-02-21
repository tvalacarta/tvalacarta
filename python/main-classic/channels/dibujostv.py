# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para dibujos.tv
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import logger
from core import config
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "dibujostv"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.dibujostv mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Series" , action="series" , url="http://series.dibujos.tv/", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Peliculas" , action="peliculas" , url="http://peliculas.dibujos.tv/", folder=True) )

    return itemlist

def series(item):
    logger.info("tvalacarta.channels.dibujostv series")
    itemlist = []

    # Extrae las series
    '''
    <div id="txtThumb">
    <div class="tt1"><a href="http://series.dibujos.tv/cosmo-trip/"><img border="0" src="http://dibujostv.estaticos.net/series/cosmo-trip/cosmo-trip_175.jpg"  width="175" class="img_list" alt="Cosmo Trip" title="Cosmo Trip"></a></div>
    <div class="tt32">
    <div class="tt4"></div>
    <div class="tt5"><a href="http://series.dibujos.tv/cosmo-trip/" class="tt6">Cosmo Trip</a></div> 
    <div class="tt7"><span id='descCorta135'>Cosmo es un extraterrestre un tanto ridículo que viaja en su destartalada nave monoplaza a través de un Universo absurdo y sorprendente. Es un Napoleón galáctico cuyo objetivo es ni más ... <img style='margin-left:5px;cursor:pointer' src='http://dibujostv.estaticos.net/images/generales/+.png' onclick='muestraDescLarga2(135);'></span><span id='descLarga135' style='display:none;'>Cosmo es un extraterrestre un tanto ridículo que viaja en su destartalada nave monoplaza a través de un Universo absurdo y sorprendente. Es un Napoleón galáctico cuyo objetivo es ni más ni menos que... ¡conquistar el Universo! Sigue sus locas aventuras cuando y como quieras en Dibujos.TV.</span></div>
    <div class="tt8"></div>
    <div style="float:left;width:180px;height:26px;background:url('http://dibujostv.estaticos.net/images/generales/fondo.listado2.png') no-repeat;margin-top:8px;padding-left:5px">
    <div style="float:left;margin-top:5px;margin-left:10px;"><a href="http://series.dibujos.tv/cosmo-trip/" class="link_favo"> Ver capítulos </a><img src="http://dibujostv.estaticos.net/images/generales/tick.paginado.png"></div>
    <div class="ict4"><img class="img_acc" src="http://dibujostv.estaticos.net/images/generales/icono.videos.png" /></div> <div class="ict5">15</div>        
    </div> 
    </div>
    </div>
    '''
    data = scrapertools.cachePage(item.url)
    patron  = '<div id="txtThumb"[^<]+'
    patron += '<div class="tt1"><a href="([^"]+)"[^<]+'
    patron += '<img border="0" src="([^"]+)"[^<]+</a></div[^<]+'
    patron += '<div class="tt32"[^<]+'
    patron += '<div class="tt4"></div[^<]+'
    patron += '<div class="tt5"><a[^>]+>([^<]+)</a></div[^<]+'
    patron += '<div class="tt7"><span id=\'descCorta\d+\'>([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    
    for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedplot in matches:
        title = scrapedtitle.strip()
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = scrapedplot.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="episodios" , url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=True ) )

    return itemlist

def peliculas(item):
    logger.info("tvalacarta.channels.dibujostv peliculas")
    itemlist = []

    # Extrae las series
    '''
    <div id="txtThumb">
    <div class="cntPel92"><a href="http://peliculas.dibujos.tv/los-viajes-de-gulliver.html" target="_blank">
    <img src="http://dibujostv.estaticos.net/peliculas/cartel-los-viajes-de-gulliver_92.jpg" width="92" height="139" style="float:left;"></a></div>
    <div class="Ptt2"> 
    <div class="Ptt3"><a href="http://peliculas.dibujos.tv/animacion/" class="Ptt3" target="_blank">Animación</a></div>        
    <div class="Ptt4"><a href="http://peliculas.dibujos.tv/los-viajes-de-gulliver.html" class="Ptt5" target="_blank">Los viajes de Gulliver</a></div>
    <div class="fr_mt5"><a class="link_tt" href="http://peliculas.dibujos.tv/los-viajes-de-gulliver.html">8</a></div><div class="Ptt12"><a href="http://peliculas.dibujos.tv/los-viajes-de-gulliver.html" class="link_tt" target="_blank"><img class="img_valo" src="http://dibujostv.estaticos.net/images/rankings/puntuacion.png" alt="Puntuación" title="Puntuación"/></a></div>
    <div class="fr_mt5"><a class="link_tt" href="http://peliculas.dibujos.tv/los-viajes-de-gulliver.html">7</a></div><div class="Ptt11"><a href="http://peliculas.dibujos.tv/los-viajes-de-gulliver.html" class="link_tt" target="_blank"><img class="img_valo" src="http://dibujostv.estaticos.net/images/generales/icono.comentarios.png" title="Comentarios" alt="Comentarios"/></a></div>
    <div class="fr_mt5"><a class="link_tt" href="http://peliculas.dibujos.tv/los-viajes-de-gulliver.html">47m 52s</a></div><div class="Ptt9"><a href="http://peliculas.dibujos.tv/los-viajes-de-gulliver.html" class="link_tt" target="_blank"><img  src="http://dibujostv.estaticos.net/images/generales/icono.duracion.png" alt="Duración" title="Duración"/></a></div> 
    <div class="Ptt6"><span id='descCorta2089'>Gulliver inicia una travesía en barco, pero en mitad del viaje su tripulación es atrapada por una tormenta y el barco se hunde. Gulliver llega hasta Liliput, una isla habitada por personas diminutas. En ella vivirá varias avent ... <img style='margin-left:5px;cursor:pointer' src='http://dibujostv.estaticos.net/images/generales/+.png' onclick='muestraDescLarga2(2089);'></span><span id='descLarga2089' style='display:none;'>Gulliver inicia una travesía en barco, pero en mitad del viaje su tripulación es atrapada por una tormenta y el barco se hunde. Gulliver llega hasta Liliput, una isla habitada por personas diminutas. En ella vivirá varias aventuras, ayudando a establecer la paz con el país vecino.</span></div>
    </div>
    </div>
    '''
    data = scrapertools.cachePage(item.url)
    patron  = '<div id="txtThumb"[^<]+'
    patron += '<div class="cntPel\d+"><a href="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)"[^<]+</a></div[^<]+'
    patron += '<div class="Ptt2"[^<]+'
    patron += '<div class="Ptt3"><a[^<]+</a></div[^<]+'
    patron += '<div class="Ptt4"><a[^>]+>([^<]+)</a></div.*?'
    patron += '<div class="Ptt6"><span id=\'desc[^\']+\'>([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedplot in matches:
        title = scrapedtitle.strip()
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = scrapedplot.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="play" , server="dibujostv" , url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=False ) )

    try:
        next_page = scrapertools.get_match(data,"<div class='pagiSiguiente'><a href='([^']+)'>")
        itemlist.append( Item( channel=item.channel , title=">> Página siguiente" , action="peliculas" , url=urlparse.urljoin(item.url,next_page) , folder=True ) )
    except:
        pass

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.dibujostv episodios")
    itemlist=[]

    if item.extra=="":
    	item.extra=item.url

    '''
    <div id="txtThumb">
    <div class="Ptt1" style="width:160px;">
    <a  href="http://series.dibujos.tv/64-zoo-lane/02-kevin-el-cocodrilo-1766.html" target="_blank"><img src="http://dibujostv.estaticos.net/series/64-zoo-lane/02-kevin-el-cocodrilo_160.jpg" alt="64 Zoo Lane - 02. Kevin, el cocodrilo" title="64 Zoo Lane - 02. Kevin, el cocodrilo" border="0" height="120" width="160" class="img_listS">    
    </a>            
    </div>
    <div class="Ptt2S" style="width:410px;"> 
    <div class="Ptt3S"><a href="http://series.dibujos.tv/64-zoo-lane/" class="Ptt3S" target="_blank">64 Zoo Lane</a></div> 
    <div class="Ptt4S"><a href="http://series.dibujos.tv/64-zoo-lane/02-kevin-el-cocodrilo-1766.html" class="Ptt5S" target="_blank">02. Kevin, el cocodrilo</a></div>
    <div class="fr_mt5" style="clear:both;"><a class="link_tt" href="http://series.dibujos.tv/64-zoo-lane/02-kevin-el-cocodrilo-1766.html">10</a></div>
    <div class="Ptt12"><a href="http://series.dibujos.tv/64-zoo-lane/02-kevin-el-cocodrilo-1766.html" class="link_tt" target="_blank"><img class="img_valo" src="http://dibujostv.estaticos.net/images/rankings/puntuacion.png" alt="Puntuación" title="Puntuación"/></a></div>
    <div class="fr_mt5"><a class="link_tt" href="http://series.dibujos.tv/64-zoo-lane/02-kevin-el-cocodrilo-1766.html">0</a></div> 
    <div class="Ptt11"><a href="http://series.dibujos.tv/64-zoo-lane/02-kevin-el-cocodrilo-1766.html" class="link_tt" target="_blank"><img class="img_valo" src="http://dibujostv.estaticos.net/images/generales/icono.comentarios.png" title="Comentarios" alt="Comentarios"/></a></div>
    <div class="fr_mt5"><a class="link_tt" href="http://series.dibujos.tv/64-zoo-lane/02-kevin-el-cocodrilo-1766.html">11m 11s</a></div>
    <div class="Ptt9"><a href="http://series.dibujos.tv/64-zoo-lane/02-kevin-el-cocodrilo-1766.html" class="link_tt" target="_blank"><img  src="http://dibujostv.estaticos.net/images/generales/icono.duracion.png" alt="Duración" title="Duración"/></a></div>
    <div class="Ptt6S">
    <span id='descLarga1766'>Kevin, el cocodrilo, intenta ser grosero a la hora de ayudar a su nuevo amigo Víctor, pero al fracasar en el intento se da cuenta que es mejor ser uno mismo.</span>                </div>
    </div>
    </div>
    '''
    '''
    <div id="txtThumb">
    <div class="Ptt1" style="width:160px;">
    <a  href="http://series-premium.dibujos.tv/edebits/14-la-decision-de-la-abuelita-1099.html" target="_blank">
    <img src="http://dibujostv.estaticos.net/series/edebits/14-la-decision-de-la-abuelita_160.jpg" alt="Edebits - 14. La decisión de la abuelita" title="Edebits - 14. La decisión de la abuelita" border="0" height="120" width="160" class="img_listS">
    <img src="http://dibujostv.estaticos.net/images/premium/iconos_premium/banda.premium.grande.png" style="position:relative;float:left;top:-130px;left:5px;" alt="Contenido Premium" title="Contenido Premium">    
    </a>            
    </div>
    <div class="Ptt2S" style="width:410px;"> 
    <div class="Ptt3S"><a href="http://series-premium.dibujos.tv/edebits/" class="Ptt3S" target="_blank">Edebits</a></div> 
    <div class="Ptt4S"><a href="http://series-premium.dibujos.tv/edebits/14-la-decision-de-la-abuelita-1099.html" class="Ptt5S" target="_blank">14. La decisión de la abuelita</a></div>
    <div class="fr_mt5" style="clear:both;"><a class="link_tt" href="http://series-premium.dibujos.tv/edebits/14-la-decision-de-la-abuelita-1099.html">0</a></div>
    <div class="Ptt12"><a href="http://series-premium.dibujos.tv/edebits/14-la-decision-de-la-abuelita-1099.html" class="link_tt" target="_blank"><img class="img_valo" src="http://dibujostv.estaticos.net/images/rankings/puntuacion.png" alt="Puntuación" title="Puntuación"/></a></div>
    <div class="fr_mt5"><a class="link_tt" href="http://series-premium.dibujos.tv/edebits/14-la-decision-de-la-abuelita-1099.html">0</a></div> 
    <div class="Ptt11"><a href="http://series-premium.dibujos.tv/edebits/14-la-decision-de-la-abuelita-1099.html" class="link_tt" target="_blank"><img class="img_valo" src="http://dibujostv.estaticos.net/images/generales/icono.comentarios.png" title="Comentarios" alt="Comentarios"/></a></div>
    <div class="fr_mt5"><a class="link_tt" href="http://series-premium.dibujos.tv/edebits/14-la-decision-de-la-abuelita-1099.html">12m 49s</a></div>
    <div class="Ptt9"><a href="http://series-premium.dibujos.tv/edebits/14-la-decision-de-la-abuelita-1099.html" class="link_tt" target="_blank"><img  src="http://dibujostv.estaticos.net/images/generales/icono.duracion.png" alt="Duración" title="Duración"/></a></div>
    <div class="Ptt6S">
    <span id='descCorta1099'>La abuela de Bet, cansada de ver su marido siempre pegado al ordenador, ha decidido separarse y venir a la base de Pangea. Bet pide ayuda a los Edebits para manipular la red de m ... <img style='margin-left:5px;cursor:pointer' src='http://dibujostv.estaticos.net/images/generales/+.png' onclick='muestraDescLarga2(1099);'></span><span id='descLarga1099' style='display:none;'>La abuela de Bet, cansada de ver su marido siempre pegado al ordenador, ha decidido separarse y venir a la base de Pangea. Bet pide ayuda a los Edebits para manipular la red de manera que su abuelo pueda volver a buscar a su mujer.</span>                </div>
    </div>
    </div>
    '''
    # Extrae los episodios
    data = scrapertools.cachePage(item.url)
    patron  = '<div id="txtThumb"[^<]+'
    patron += '<div class="Ptt1"[^<]+'
    patron += '<a\s*href="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)"(.*?)'
    patron += '<div class="Ptt2S"[^<]+'
    patron += '<div class="Ptt3S"><a[^>]+>([^<]+)</a></div[^<]+'
    patron += '<div class="Ptt4S"><a[^>]+>([^<]+)</a></div.*?'
    patron += '<span id=\'desc[^\']+\'>([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,resto,scrapedshow,scrapedtitle,scrapedplot in matches:
        title = scrapedshow.strip()+" "+scrapedtitle.strip()
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = scrapedplot.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        if "Contenido Premium" in resto:
            title = title + " (premium)"
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="play" , server="dibujostv" , url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=False ) )

    try:
        next_page = scrapertools.get_match(data,"<div class='pagiSiguiente'><a href='([^']+)'>")
        #itemlist.append( Item( channel=item.channel , title=">> Página siguiente" , action="episodios" , url=urlparse.urljoin(item.url,next_page) , folder=True ) )
        next_page_item = Item( channel=item.channel , title=">> Página siguiente" , action="episodios" , url=urlparse.urljoin(item.url,next_page) , extra=item.extra, folder=True )
        itemlist.extend( episodios(next_page_item) )
    except:
    	#en la última página añade la entrada de "Opciones para esta serie"
        if config.is_xbmc() and len(itemlist)>0:
            itemlist.append( Item(channel=item.channel, title=">> Opciones para esta serie", url=item.extra, action="serie_options##episodios", thumbnail=item.thumbnail , show=item.show, folder=False))

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    
    # El canal tiene estructura programas -> episodios -> play
    items_mainlist = mainlist(Item())
    items_programas = []

    # Todas las opciones del menu tienen que tener algo
    for item_mainlist in items_mainlist:
        exec "itemlist="+item_mainlist.action+"(item_mainlist)"
    
        if len(itemlist)==0:
            print "La sección '"+item_mainlist.title+"' no devuelve nada"
            return False

        if item_mainlist.action=="series":
            items_programas = itemlist

    # Ahora recorre los programas hasta encontrar vídeos en alguno
    for item_programa in items_programas:
        print "Verificando "+item_programa.title
        items_episodios = episodios(item_programa)

        if len(items_episodios)>0:
            return True

    print "No hay videos en ningún programa"
    return False
