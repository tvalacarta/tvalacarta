# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Azteca 13 (México)
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import config
from core import logger
from core import scrapertools
from core import jsontools
from core.item import Item

DEBUG = config.get_setting("debug")
CHANNELNAME = "azteca13"
PROGRAMAS_URL = "http://www.aztecatrece.com/"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.azteca13 mainlist")

    return programas(Item(channel=CHANNELNAME))

def programas(item):
    logger.info("tvalacarta.channels.azteca13 programas")

    itemlist = []

    if item.url=="":
        item.url=PROGRAMAS_URL

    data = scrapertools.cache_page(item.url)
    logger.info("tvalacarta.channels.azteca13 data="+data)

    '''
    <!-- MENU DEL SITIO -->
    <a href="javascript:" class="ztkTbAcTog"><i class="fa fa-smile-o"></i>
    ENTRETENIMIENTO<i class="fa fa-angle-down"></i></a>
    <div class="ztkTbAcEl">
    <a href="/alextremo">Al Extremo</a>
    <a href="/boom">Boom</a><a href="/escapeperfecto">Escape perfecto</a><a href="/lastardesconlabigorra">Las Tardes con la Bigorra</a><a href="/masterchef">MasterChef 2016</a><a href="/masterchefjunior">MasterChef Junior</a><a href="/nopierdaselbillete">No pierdas el billete</a><a href="/quehaydecomer">Qué hay de comer</a><a href="/todoonada">Todo o nada</a><a href="/vengaeldomingo">Venga el domingo</a><a href="/vengalaalegria">Venga la alegría</a></div> <a href="javascript:" class="ztkTbAcTog"><i class="fa fa-tv"></i>
    TELENOVELAS<i class="fa fa-angle-down"></i></a><div class="ztkTbAcEl"><a href="/acadaquiensusanto">A cada quien su santo</a><a href="/aztecanovelasonline">Azteca Novelas Online</a><a href="/boogieoogie">Boogie Oogie</a><a href="/celia">Celia</a><a href="/cuandoseasmia">Cuando seas mía</a><a href="/estanentrenosotros">Están entre nosotros</a><a href="/hastaqueteconoci">Hasta que te conocí</a><a href="/lafiscaldehierro">La Fiscal de Hierro</a><a href="/lavidaenelespejo">La vida en el espejo</a><a href="/loquecallamos">Lo que callamos las mujeres</a><a href="/rosariotijeras">Rosario Tijeras</a><a href="/secretos">Secretos</a><a href="/undiacualquiera">Un día cualquiera</a><a href="/visavis">Vis a Vis</a></div> <a href="javascript:" class="ztkTbAcTog"><i class="fa fa-ticket"></i>ESPECTáCULOS<i class="fa fa-angle-down"></i></a><div class="ztkTbAcEl"><a href="/lahistoriadetrasdelmito">La Historia Detrás del Mito</a><a href="/laresolanaconelcapi">La resolana con el Capi</a><a href="/ventaneando">Ventaneando</a></div> <a href="javascript:" class="ztkTbAcTog"><i class="fa fa-newspaper-o"></i>NOTICIAS<i class="fa fa-angle-down"></i></a><div class="ztkTbAcEl"><a href="http://www.aztecanoticias.com.mx/am/index/index">Hechos AM TVA</a><a href="http://www.aztecanoticias.com.mx/hechos-meridiano">Hechos meridiano</a><a href="http://www.aztecanoticias.com.mx/hechos-noche">Hechos noche</a><a href="http://www.aztecanoticias.com.mx/hechos-sabado">Hechos sábado</a></div> <a href="javascript:" class="ztkTbAcTog"><i class="fa fa-film"></i>PELÍCULAS<i class="fa fa-angle-down"></i></a><div class="ztkTbAcEl"><a href="/cinetrece">Cine Trece</a></div> <a href="javascript:" class="ztkTbAcTog"><i class="fa fa-comment-o"></i>AZTECA OPINION<i class="fa fa-angle-down"></i></a><div class="ztkTbAcEl"><a href="/13-en-libertad">13 en libertad</a><a href="/a-quemarropa">A quemarropa</a><a href="/al-filo">Al filo</a><a href="/aqui-entre-amigos">Aquí entre amigos</a><a href="/berman-otras-historias">Berman otras historias</a><a href="/camara-libre">Cámara libre</a><a href="/de-la-cepa-a-la-mesa">De la cepa a la mesa</a><a href="/desafio">Desafío</a><a href="/desafio-global">Desafío Global</a><a href="/ec-pablo-boullosa">EC Pablo Boullosa</a><a href="/el-nuevo-mexico">El Nuevo México</a><a href="/el-otro-palco">El otro palco</a><a href="/en-contexto">En contexto</a><a href="/encuentro-de-opiniones">Encuentro de opiniones</a><a href="/entre-lineas">Entre líneas</a><a href="/entre-reporteros">Entre reporteros</a><a href="/frente-a-frente">Frente a frente</a><a href="/katia360">Katia 360</a><a href="/la-billetera">La billetera</a><a href="/la-columna-de-paco-rodriguez">La Columna de Paco Rodríguez</a><a href="/la-de-8">La de ocho</a><a href="/la-entrevista-con-sarmiento">La entrevista con Sarmiento</a><a href="/la-pura-verdad">La pura verdad</a><a href="/las-finanzas-con-dario-celis">Las finanzas con Dario Celis</a><a href="/los-corresponsales">Los corresponsales</a><a href="/los-despachos-del-poder">Los despachos del poder</a><a href="/mexico-confidencial">México confidencial</a><a href="/observadores">Observadores</a><a href="/periferico-1313">Periferico 1313</a><a href="/Primer-circulo">Primer círculo</a><a href="/reporte-13">Reporte 13</a><a href="/rocha-y-sarmiento">Rocha y Sarmiento</a><a href="/serpientes-y-escaleras">Serpientes y escaleras</a><a href="/tocando-vidas">Tocando vidas</a><a href="/un-minuto-con-el-arte">Un minuto con el arte</a><a href="/una-mujer-en-la-historia">Una mujer en la historia</a><a href="/vidas-apasionantes">Vidas apasionantes</a></div> <a href="javascript:" class="ztkTbAcTog"><i class="fa fa-recycle"></i>Sigue viendo<i class="fa fa-angle-down"></i></a><div class="ztkTbAcEl"><a href="http://www.aztecatrece.com/aztecanovelasonline">Azteca Novelas Online</a><a href="http://eltrece.mx/Consellodemujer">Con sello de mujer</a><a href="http://www.eltrece.mx/famososenjaque">Famosos en jaque</a><a href="http://eltrece.mx/HistoriasEngarzadas">Historias engarzadas</a><a href="http://www.eltrece.mx/lahistoriadetrasdelmito">La historia detrás del mito</a><a href="http://www.aztecatrece.com/loquelagentecuenta">Lo que la gente cuenta</a><a href="http://eltrece.mx/traslasrejas">Tras las rejas</a><a href="http://aztecatrece.com/vidasallimite">Vidas al límite</a></div>
    <!-- FIN MENU DEL SITIO --> 
    '''

    data = scrapertools.find_single_match(data,'<!-- MENU DEL SITIO -->(.*?)<!-- FIN MENU DEL SITIO -->')

    patron = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.strip()
        thumbnail = ""
        plot = ""
        url = "http://www.aztecatrece.com/"+scrapedurl+"/historico/programas-completos"
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="episodios", url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail, view="videos" ) )

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.page)

    item.plot = scrapertools.find_single_match(data,'<article class="span8"[^<]+<div class="contenido_noticia">(.*?)</div>')
    item.plot = scrapertools.htmlclean(item.plot).strip()

    item.thumbnail = scrapertools.find_single_match(data,'<img src="([^"]+)" alt="" class="img-det-not">')

    #item.title = scrapertools.find_single_match(data,'<article class="span8"[^<]+<h2>([^<]+)</h2>')

    return item

def episodios(item):
    logger.info("tvalacarta.channels.azteca13 episodios")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    patron  = '<div[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img width="\d+" height="\d+" src="([^"]+)"[^<]+'
    patron += '</a[^<]+'
    patron += '<a href="[^"]+"><i[^<]+</i><h2[^>]+>([^<]+)</h2></a[^<]+'
    patron += '<h4>([^<]+)</h4[^<]+'
    patron += '<p>([^<]+)</p'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle,fecha,scrapedplot in matches:
        title = scrapedtitle.strip()+" "+fecha.strip()
        thumbnail = scrapedthumbnail
        plot = scrapedplot
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="play", server="azteca", url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail, folder=False ) )

    if len(itemlist)==0 and "programas-completos" in item.url:
        item.url = item.url.replace("programas-completos","capitulos")
        return episodios(item)

    return itemlist

def detalle_episodio(item):

    item.geolocked = "0"
    
    try:
        from servers import azteca as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def play(item):

    item.server="azteca";
    itemlist = [item]

    return itemlist

# Test de canal
# Devuelve: Funciona (True/False) y Motivo en caso de que no funcione (String)
def test():
    
    # Carga el menu principal
    items_programas = mainlist(Item())

    if len(items_programas)==0:
        return False,"No hay programas"

    for item_programa in items_programas:
        items_episodios = episodios(item_programa)
        if len(items_episodios)>0:
            break

    if len(items_episodios)==0:
        return False,"No hay episodios"

    item_episodio = detalle_episodio(items_episodios[0])
    if item_episodio.media_url=="":
        return False,"El conector no devuelve enlace para el vídeo "+item_episodio.title

    return True,""
