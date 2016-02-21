# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para tvolucion.com
# creado por lpedro aka cuatexoft
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools
from servers import youtube

__channel__ = "tvolucion"
__category__ = "F"
__type__ = "generic"
__title__ = "tvolucion"
__language__ = "ES"
__creationdate__ = "20111014"
__vfanart__ = "http://img594.imageshack.us/img594/7788/fanart.png"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[tvolucion.py] mainlist")
    
    itemlist = []
    #   itemlist.append( Item(channel=__channel__, title="Buscar" , action="search") )
    itemlist.append( Item(channel=__channel__, title="Cine", action="cine", url="http://tvolucion.esmas.com/entretenimiento/noticias/cine/", thumbnail="http://img690.imageshack.us/img690/690/cinev.png", fanart = __vfanart__)) 
    itemlist.append( Item(channel=__channel__, title="Deportes", action="deportes", url="http://televisadeportes.esmas.com/video/", thumbnail="http://img217.imageshack.us/img217/2709/deportesk.png", fanart = __vfanart__)) 
    itemlist.append( Item(channel=__channel__, title="Novelas Recientes", action="novelasr", url="http://tvolucion.esmas.com/secciones.php?canal=telenovelas", thumbnail="http://img651.imageshack.us/img651/4894/novelasq.png", fanart = __vfanart__))
    itemlist.append( Item(channel=__channel__, title="Novelas Anteriores", action="novelasa", url="http://tvolucion.esmas.com/secciones.php?canal=telenovelas", thumbnail="http://img607.imageshack.us/img607/4232/novelasa.png", fanart = __vfanart__))
    itemlist.append( Item(channel=__channel__, title="Programas", action="programas", url="http://tvolucion.esmas.com/secciones.php?canal=programas-de-tv", thumbnail="http://img845.imageshack.us/img845/9910/40000175.png", fanart = __vfanart__))
    itemlist.append( Item(channel=__channel__, title="Kids", action="ninos", url="http://www2.esmas.com/chicoswaifai/videos/", thumbnail="http://img267.imageshack.us/img267/6987/kidsg.png", fanart = __vfanart__)) 
    itemlist.append( Item(channel=__channel__, title="Noticias", action="noticias", url="http://tvolucion.esmas.com/secciones.php?canal=noticieros", thumbnail="http://img827.imageshack.us/img827/1724/noticiasir.png", fanart = __vfanart__)) 
    # itemlist.append( Item(channel=__channel__, title="Todas las Novelas (Prueba)", action="novelas", url="http://www.tutelenovela.net/p/telenovelas.html", thumbnail="", fanart = __vfanart__)) 
    itemlist.append( Item(channel=__channel__, title="En Vivo", action="tv", url="http://www.ilive.to/view/1598/", thumbnail="http://img716.imageshack.us/img716/9962/canal10.png", fanart = __vfanart__)) 
# itemlist.append( Item(channel=__channel__, title="Teresa", action="teresa", url="http://blog.cuatexoft.com/?p=537")) 
    # http://tvolucion.esmas.com/home_mas_visto.php
    return itemlist

def cine(item):
    logger.info("[tvolucion.py] cine")
    
    # Descarga la p‡gina
    data = scrapertools.cachePage(item.url)
    extra = item.extra
    
    # Extrae las entradas de la pagina seleccionada
    '''
        style="padding-left:7px;"><a href="http://televisadeportes.esmas.com/video/
        
        '''
    
    patron = '<tr.*?>.*?<td><a href="([^"]+)">([^<]+)</a></td>.*?<td>([^<]+)</td>.*?<td>([^<]+)</td>.*?<td>([^<]+)</td>.*?</tr>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        scrapedurl = match[0]
        scrapedtitle = match[1]
        scrapedthumbnail = "http://www.tvyespectaculos.com/wp-content/uploads/2010/07/Televisa.jpg"
        scrapedplot = match[2]+chr(10)+"DURACION : "+match[3]+chr(10)+"AGREGADO : "+match[4]+chr(10)+scrapedurl
        logger.info(scrapedtitle)
        # baja thumbnail
        data2 = scrapertools.cachePage(scrapedurl)
        patron2 = 'videoImgFrame=\'(.*?)\';.*?videoUrlFrame=\'(.*?)\';'
        matches2 = re.compile(patron2,re.DOTALL).findall(data2)
        for match2 in matches2:
            scrapedthumbnail = match2[0]
            scrapedplot = scrapedplot +chr(10)+scrapedthumbnail
        
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="video", title=scrapedtitle.upper() , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) )
    
    return itemlist

def ninos(item):
    logger.info("[tvolucion.py] ninos")
    
    # Descarga la p‡gina
    data = scrapertools.cachePage(item.url)
    extra = item.extra
    scrapedfanart = "NO"

    patron = '<div class="col-15 padding-L10 padding-T20">(.*?)</div>.*?<a class="thumbImgBorder" href="([^"]+)".*?<img src="([^"]+)" width="235" height="96"></a>'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        scrapedurl = match[1]
        scrapedtitle = match[0]
        scrapedthumbnail = match[2]
        scrapedplot = ""
        logger.info(scrapedtitle)
        
        # baja fanart
        data2 = scrapertools.cachePage(scrapedurl)
        patron2 = '<img src="([^"]+)" class="stage.*?>(.*?)</div>'
        matches2 = re.compile(patron2,re.DOTALL).findall(data2)
        for match2 in matches2:
            scrapedfanart = match2[0]
        #baja plot
        patron3 = '<div class="info" style=.*?<h3>(.*?)</h3>.*?<h4>(.*?)</h4>.*?<h5>(.*?)</h5>'
        matches3 = re.compile(patron3,re.DOTALL).findall(data2)
        for match3 in matches3:
            scrapedplot = match3[0] #+chr(10)+match2[1] +chr(10)+match2[2] +chr(10)+match2[3] +chr(10)+match2[4] 
        
        
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="capitulo", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , fanart=scrapedfanart,  plot=scrapedplot , extra=extra , folder=True) )
    
    
    return itemlist



def deportes(item):
    logger.info("[tvolucion.py] deportes")
    
    # Descarga la p‡gina
    data = scrapertools.cachePage(item.url)
    extra = item.extra
    
    # Extrae las entradas de la pagina seleccionada
    '''
       style="padding-left:7px;"><a href="http://televisadeportes.esmas.com/video/
        
        '''
    
    patron = '</div><br><a href="http://televisadeportes.esmas.com/video/(.*?)/".*?class="(.*?)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        scrapedurl = "http://televisadeportes.esmas.com/video/"+match[0]+"/"
        scrapedtitle = match[0]
        scrapedthumbnail = "http://www.tvyespectaculos.com/wp-content/uploads/2010/07/Televisa.jpg"
        scrapedplot = "El mejor contenido de videos deportivos, en exclusiva por internet."+chr(10)+scrapedurl
        logger.info(scrapedtitle)
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="deportescap", title=scrapedtitle.upper() , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) )
    
    patron = 'style="padding-left:7px;"><a href="http://televisadeportes.esmas.com/video/(.*?)/(.*?)".*?class'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
#itemlist = []
    for match in matches:
        scrapedurl = "http://televisadeportes.esmas.com/video/"+match[0]+"/"+match[1]
        scrapedtitle = match[0] +" - "  + match[1][0:len(match[1])-1]
        scrapedthumbnail = "http://www.tvyespectaculos.com/wp-content/uploads/2010/07/Televisa.jpg"
        scrapedplot = "El mejor contenido de videos deportivos, en exclusiva por internet."+chr(10)+scrapedurl
        logger.info(scrapedtitle)
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="deportescap", title=scrapedtitle.upper() , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) )  

    return itemlist

def deportescap(item):
    logger.info("[tvolucion.py] deportescap")
    
    # Descarga la p‡gina
    data = scrapertools.cachePage(item.url)
    extra = item.extra
    #  COLECCION PRIVADA
    # Extrae las entradas de la pagina seleccionada
    '''
        <li><span class="chaptersLongTitle">
        <a href='http://televisadeportes.esmas.com/video/noticias/172742/coleccion-privada-golazos-santos' class="txtColor4 txtMedium">Colecci—n Privada: Golazos de Santos</a>
        </span>
        <span class="chaptersLen">00:01:24</span></li>	
        <li><span class="chaptersLongTitle">
        <a href='http://televisadeportes.esmas.com/video/noticias/172735/coleccion-privada-golazos-rayados' class="txtColor4 txtMedium">Colecci—n Privada: Golazos de Rayados</a>

        
        '''

    
    #thumbnails
    patron = '<img class="thumbImageSizer" style="border:medium none; position:absolute;" src="([^"]+)"/>.*?<div class="playOverIcon" id="playOverIcon1_00" style="display:none;">.*?<a href=\'(.*?)\'>.*?<img src="http://i2.esmas.com/tvolucion/img/thumb_ico_play.gif" />.*?<\a>.*?<\div>.*?<div style="position:absolute;" onMouseOut="showhideplay.*?" onMouseOver="showhideplay.*?" class="TipsMask" title="<ul><li style=\'width:11px; height:40px; background-image:url(http://i2.esmas.com/tvolucion/img/piquito.gif); background-position:top; background-repeat:no-repeat; float:left;\'></li><li style=\'float:left; background-color:#E2E2E2; width:300px;\'><ul><li class=\'txtMedium txtColor3 txtBold left\' style=\'padding: 3px 10px 3px 10px;\'>([^<]+)</li><li class=\'txtMedium txtColor3 txtNormal left\' style=\'padding: 3px 10px 3px 10px;\'>([^<]+)</li><li class=\'txtSmall txtColor1 txtNormal left\' style=\'padding: 3px 10px 3px 10px;\'>([^<]+)</li></ul></li></ul>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        scrapedurl = match[1]
        scrapedtitle = match[2] + " - " + match[3]
        scrapedthumbnail = match[0]
        scrapedplot = match[2] + " - " + match[3] + chr(10) + match[4]
        logger.info(scrapedtitle)
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="video", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) )
    
    #LISTADO ANTIGUO
    patron = 'style="background-image:url\((.*?)\);">.*?<a href="([^"]+)">.*?<img id="playOverIcon0_.*?" class="TipsMask3 playOverIcon" style="display:none;" onMouseOver="Javascript:keep_rollover.*?onMouseOut="Javascript:keep_rollover.*?src="http://i2.esmas.com/tvolucion/img/thumb_ico_play.gif" title="<ul style=\'list-style:none;\'><li style=\'width:11px; height:40px; background-image:.*?background-position:top; background-repeat:no-repeat; float:left;\'></li><li style=\'float:left; background-color:#E2E2E2; width:300px;\'><ul style=\'list-style:none;\'><li class=\'txtMedium txtColor1 txtBold left\' style=\'padding: 3px 10px 3px 10px;\'>([^<]+)</li><li class=\'txtMedium txtColor1 txtNormal left\' style=\'padding: 3px 10px 3px 10px;\'>([^<]+)</li><li class=\'txtSmall txtColor1 txtNormal left\' style=\'padding: 3px 10px 3px 10px;\'>([^<]+)</li></ul></li></ul>"/>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
#itemlist = []
    for match in matches:
        scrapedurl = match[1]
        scrapedtitle = match[2] + " - " + match[3]
        scrapedthumbnail = match[0]
        scrapedplot = match[2] + " - " + match[3] + chr(10) + match[4]
        logger.info(scrapedtitle)
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="video", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) )

    #LISTADO NUEVO
    patron = '<li><span class="chaptersLongTitle">.*?<a href=\'http://televisadeportes.esmas.com/video/(.*?)\' class="txtColor4 txtMedium">([^<]+)</a>.*?</span>.*?<span class="chaptersLen">([^<]+)</span></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
#itemlist = []
    for match in matches:
        scrapedurl = "http://televisadeportes.esmas.com/video/"+match[0]
        scrapedtitle = match[1]
        scrapedthumbnail = "http://www.tvyespectaculos.com/wp-content/uploads/2010/07/Televisa.jpg"
        scrapedplot = match[1]+chr(10)+"DURACION: "+match[2]+chr(10)+scrapedurl
        logger.info(scrapedtitle)
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="video", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) ) 
       
    #temporadas
    patron = '<span class="seasonInfo">([^<]+)</span>.*?<span class="chaptersTitle"><a href="([^"]+)" class="txtColor4 txtMedium">([^<]+)</a></span>.*?<span class="chaptersLen">([^<]+)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
#itemlist = []
    for match in matches:
        scrapedurl = match[1]
        scrapedtitle = match[0] + " - " + match[2]
        scrapedthumbnail = "http://www.tvyespectaculos.com/wp-content/uploads/2010/07/Televisa.jpg"
        scrapedplot = match[0] + " - " + match[2] + chr(10)+" DURACION : "+match[3]
        logger.info(scrapedtitle)
    
    # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="video", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) )
   
  
    return itemlist


def novelas(item):
    logger.info("[tvolucion.py] novelas")
    
    # Descarga la p‡gina
    data = scrapertools.cachePage(item.url)
    extra = item.extra
    
    # Extrae las entradas de la pagina seleccionada
    '''
        <a class="ttn-list" href="http://tutelenovela.blogspot.com/2011/05/telenovela-corazon-abierto.html" title="A Corazon abierto"><div class="im"><img src="http://www.appelsiini.net/projects/lazyload/img/grey.gif" data-original="http://www.estadisco.com/tutelenovela/cover-novelas/a-corazon-abierto.jpg" /></div><div class="des"><span class="title">A Corazon abierto</span><span class="year">www.tutelenovela.net</span><span class="rep">Ver Capitulos de A Corazon abierto.</span></div></a>

    '''
    
    patron = '<a class="ttn-list" href="(.*?)" title="([^<]+)"><div class="im"><img src="http://www.appelsiini.net/projects/lazyload/img/grey.gif" data-original="([^"]+)" /></div>'#<div class="im">.*?data-original="([^"]+)"/></a>'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        scrapedurl = match[0]
        scrapedtitle = match[1]
        scrapedthumbnail = match[2]
        scrapedplot = match[0]
        logger.info(scrapedtitle)
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="capitulo2", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) )
    
    return itemlist


def capitulo2(item):
    logger.info("[tvolucion.py] capitulo2")
    
    # Descarga la p‡gina
    data = scrapertools.cachePage(item.url)
    data.replace("<b>","")
    extra = item.extra
    
    # Extrae las entradas de la pagina seleccionada
    '''<a href="http://www.tutelenovela.net/2012/06/abismo-de-pasion-cap-97.html" style="background: orange;">Abismo de Pasion - Capitulo 97</a><br>
        <a href="http://www.tutelenovela.net/2012/06/abismo-de-pasion-cap-96.html" style="background: orange;">Abismo de Pasion - Capitulo 96</a><br>
        <a href="http://www.tutelenovela.net/2012/06/abismo-de-pasion-cap-95.html" style="background: #ccff00;">Abismo de Pasion - Capitulo 95</a><br> 
        
        <a href="http://www.tutelenovela.info/teresa/800/capitulo-1.html">Teresa ~ Capitulo-1</a><br />
        <a href="http://www.tutelenovela.info/teresa/801/capitulo-2.html">Teresa ~ Capitulo-2</a><br />
        
        <a href="http://www.tutelenovela.net/2011/07/los-20-momentos-mas-importantes-de-la.html" style="background: orange;"><b>LOS 20 MOMENTOS MAS IMPORTANTES</b> | La Reina del Sur | TuTeleNovela.Net</a><br />
        <a href="http://www.tutelenovela.net/2011/06/kate-del-castillo-y-teresa-entrevista.html" style="background: yellow;"><b>KATE DEL CASTILLO Y TERESA ENTREVISTA</b> | La Reina del Sur | TuTeleNovela.Net</a><br />
        <a href="http://www.tutelenovela.net/2011/06/entrevista-kate-del-castillo-la-reina.html" style="background: ccffdd;"><b>ENTREVISTA A KATE DEL CASTILLO</b> | La Reina del Sur | TuTeleNovela.Net</a><br />
        <a href="http://www.tutelenovela.net/2011/06/especial-con-los-actores-de-la-reina.html" style="background: pink;"><b>ESPECIAL CON LOS ACTORES</b> | La Reina del Sur | TuTeleNovela.Net</a><br />
        <a href="http://www.tutelenovela.net/2011/05/especial-con-cristina-de-la-reina-del.html" style="background: skyblue;"><b>ESPECIAL CON CRISTINA</b> | La Reina del Sur | TuTeleNovela.Net</a><br />
        <a href="http://www.tutelenovela.net/2011/05/telenovela-la-reina-del-sur-capitulo-63.html" style="background: yellow;">Capitulo 63 <b>[GRAN FINAL!!!]</b> | La Reina del Sur | TuTeleNovela.Net</a><br />
        <a href="http://tutelenovela.blogspot.com/2011/05/telenovela-la-reina-del-sur-capitulo-62.html">Capitulo 62 | La Reina del Sur | TuTeleNovela.Net</a><br />        
        '''
    #ESPECIALES
    # patron = '<td><a href="http://tvolucion.esmas.com/telenovelas/([^"]+)">([^<]+)</a>.*?<td>'
    patron = '<a href="([^"]+)" style=".*?"><b>([^<]+)<.*?<br'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        scrapedurl = match[0]
        scrapedtitle = match[1]
        scrapedthumbnail = item.thumbnail
        scrapedplot = match[0]
        logger.info(scrapedtitle)
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="video2", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) )
    
    # CAPITULOS
    # patron = '<td><a href="http://tvolucion.esmas.com/telenovelas/([^"]+)">([^<]+)</a>.*?<td>'
    
    patron = '<a href="([^"]+)" style=".*?">([^<]+)<.*?<b'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    # itemlist = []
    for match in matches:
        scrapedurl = match[0]
        scrapedtitle = match[1]
        scrapedthumbnail = item.thumbnail
        scrapedplot =match[0]
        logger.info(scrapedtitle)
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="video2", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) )
    
    # CAPITULOS .INFO
    patron = '<a href="http://www.tutelenovela.info/(.*?)">(.*?)</a><br'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    # itemlist = []
    for match in matches:
        scrapedurl = "http://www.tutelenovela.info/"+match[0]
        scrapedtitle = match[1]
        scrapedthumbnail = item.thumbnail
        scrapedplot = "http://www.tutelenovela.info/"+match[0]
        logger.info(scrapedtitle)
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="video2", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) )

     # CAPITULOS BLOGSPOT 
    patron = '<a href="http://tutelenovela.blogspot.com/(.*?)">(.*?)</a><br'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    # itemlist = []
    for match in matches:
        scrapedurl = "http://tutelenovela.blogspot.com/"+match[0]
        scrapedtitle = match[1]
        scrapedthumbnail = item.thumbnail
        scrapedplot = "http://tutelenovela.blogspot.com/"+match[0]
        logger.info(scrapedtitle)
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="video2", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) )


    return itemlist


def video2(item):
    logger.info("[tvolucion.py] video2")
    
    # Descarga la p‡gina
    data = scrapertools.cachePage(item.url)
    extra = item.extra
    
    # Extrae las entradas de la pagina seleccionada
    '''<div id="codtv" style="display:none;">
        <embed type="application/x-shockwave-flash" src="http://data.tutelenovela.info/player2.swf" style="" id="mpl" name="mpl" quality="high" allowfullscreen="true" allowscriptaccess="always" flashvars="skin=&amp;plugins=fbit-1,tweetit-1,plusone-1,adttext&amp;file=mp4:/m4v/boh/abism/abism-c095/abism-c095-480&amp;streamer=rtmp://bright.tvolucion.com/ondemand/files/&amp;autostart=false&amp;adttext.config=http://http://data.tutelenovela.info/news.xml&amp;stretching=fill&amp;image=http://2.bp.blogspot.com/-8UbEL3s3LTw/TjHXDeARqsI/AAAAAAAAASw/ljTThn5olco/s1600/logoimage.jpg&amp;logo.file=http://4.bp.blogspot.com/-BqIUzzfYxFQ/TjHYQTa66KI/AAAAAAAAAS4/sxsPtxTnhZk/s1600/logoplayer.png&amp;logo.hide=false&amp;logo.position=top-left&amp;logo.link=http://www.tutelenovela.net&amp;abouttext=TUTELENOVELA.NET - Telenovelas y Series!&amp;aboutlink=http://www.tutelenovela.net/" height="450" width="700"> </div>
        
        rtmp://bright.tvolucion.com/ondemand/files/m4v/mp4:tln/t1-c101-desti/t1-c101-desti-150.mp4
        '''
    patron = 'file=mp4:(.*?)&amp;streamer=rtmp://(.*?)/files/&amp;'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        #scrapedurl = "rtmp://bright.tvolucion.com/ondemand/files/m4v/tln/t1-c101-desti/t1-c101-desti-150.mp4"
        scrapedurl = "rtmp://"+match[1]+"/files"+match[0]+".mp4"
        scrapedurlhd = scrapedurl.replace("-480.mp4","-600.mp4")
        scrapedtitle =  item.title
        scrapedthumbnail = item.thumbnail
        scrapedplot = "rtmp://"+match[1]+"/files"+match[0]+".mp4"
        logger.info(scrapedtitle)
        
        # A–ade al listado
        # CALIDAD MEDIA
        itemlist.append( Item(channel=__channel__, action="play", title=scrapedtitle + " CALIDAD MEDIA ", url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) )        
        # CALIDAD HD
        itemlist.append( Item(channel=__channel__, action="play", title=scrapedtitle + " CALIDAD HD ", url=scrapedurlhd , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) )
    
    
    
    # PARA BUSCAR FLV

    '''<div class="vvplayer">
    <embed type='application/x-shockwave-flash' src='http://www.4shared.com/flash/player.swf' width='533' height='380' bgcolor='undefined' allowscriptaccess='always' allowfullscreen='true' wmode='transparent' flashvars='file=http://content2.catalog.video.msn.com/e2/ds/es-us/ESUS_Telemundo_Network/ESUS_Telemundo_La_Reina_del_Sur/e4962e44-1b59-4e0e-815e-ce967a79c3bc.flv&autostart=false&image=http://t1.gstatic.com/images?q=tbn:ANd9GcTO20FJSfFugNVmix_MOD3f9_rRO6VQfjygp4EY3Bfk0JIPu8hr&t=1&link=http://www.tutelenovela.net/&backcolor=000000&frontcolor=EEEEEE&lightcolor=FFFFFF&logo=http://4.bp.blogspot.com/-BqIUzzfYxFQ/TjHYQTa66KI/AAAAAAAAAS4/sxsPtxTnhZk/s1600/logoplayer.png&image=http://2.bp.blogspot.com/-8UbEL3s3LTw/TjHXDeARqsI/AAAAAAAAASw/ljTThn5olco/s1600/logoimage.jpg&volume=100&controlbar=over&stretching=exactfit'/></embed>
    </div>'''
    
    
    patron = '<embed type=.*?file=(.*?)flv(.*?)=false.*?</embed>'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
# itemlist = []
        
    for  match in matches:
        
        #scrapedurl = "rtmp://bright.tvolucion.com/ondemand/files/m4v/tln/t1-c101-desti/t1-c101-desti-150.mp4"
        scrapedurl = match[0]+"flv"
        scrapedtitle =  item.title
        scrapedthumbnail = item.thumbnail
        scrapedplot = match[0]+"flv"
        logger.info(scrapedtitle)
        
        # A–ade al listado
        
        # CALIDAD MEDIA
        itemlist.append( Item(channel=__channel__, action="play", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) )
                      


    return itemlist

def novelasr(item):
    logger.info("[tvolucion.py] novelasr")
    
    # Descarga la p‡gina
    data = scrapertools.cachePage(item.url)
    extra = item.extra
    scrapedfanart = "NO"
    
    # Extrae las entradas de la pagina seleccionada
    '''<li>
		<a href="http://tvolucion.esmas.com/telenovelas/romantica/amor-bravio"><img src="http://i2.esmas.com/buttons/2012/03/01/25394/170x128.jpg" alt="Amor Brav’o"></a>
		<h3>Amor Brav’o</h3>
		<h4>2012</h4>
        </li>	
        
        http://i2.esmas.com/img/espectaculos3/telenovelas/abismo-de-pasion/backArriba_usa.jpg
        http://i2.esmas.com/img/espectaculos3/telenovelas/cachitoDeCielo/back.jpg
        '''
    
    patron = '<a href="http://tvolucion.esmas.com/telenovelas/([^"]+)"><img src="([^"]+)" alt="([^"]+)"></a>'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        #scrapedurl1 = "http://m.tvolucion.esmas.com/telenovelas/"+match[0]
        scrapedurl1 = "http://tvolucion.esmas.com/telenovelas/"+match[0]
        string = match[0]+" "
        print "cadena " +string
        print string.find("/ ")
        if int(string.find("/ "))<0:
            scrapedurl = "http://googleak.esmas.com/search?q=site:http://tvolucion.esmas.com/telenovelas/"+match[0]+"&btnG=Google+Search&access=p&client=masarchivo&site=portal&output=xml_no_dtd&proxystylesheet=tv3vidrecientes&entqrm=0&oe=UTF-8&ie=UTF-8&ud=1&exclude_apps=1&getfields=*&num=25&sort=date:D:L:d1&entqr=6&filter=0&ip=189.254.126.103,63.99.211.110&start=0"
        else:
            string =string[0:string.find("/ ")]
            scrapedurl = "http://googleak.esmas.com/search?q=site:http://tvolucion.esmas.com/telenovelas/"+string+"&btnG=Google+Search&access=p&client=masarchivo&site=portal&output=xml_no_dtd&proxystylesheet=tv3vidrecientes&entqrm=0&oe=UTF-8&ie=UTF-8&ud=1&exclude_apps=1&getfields=*&num=25&sort=date:D:L:d1&entqr=6&filter=0&ip=189.254.126.103,63.99.211.110&start=0"
        print scrapedurl
        scrapedtitle = match[2]
        scrapedthumbnail = match[1]
        scrapedplot = scrapedurl
        logger.info(scrapedtitle)
        
        # baja fanart
        data2 = scrapertools.cachePage(scrapedurl1)
        patron2 = '<img src="([^"]+)" class="stage.*?>(.*?)</div>'
        matches2 = re.compile(patron2,re.DOTALL).findall(data2)
        for match2 in matches2:
            scrapedfanart = match2[0]
        #baja plot
        patron3 = '<div class="info" style=.*?<h3>(.*?)</h3>.*?<h4>(.*?)</h4>.*?<h5>(.*?)</h5>'
        matches3 = re.compile(patron3,re.DOTALL).findall(data2)
        for match3 in matches3:
            scrapedplot = match3[0] #+chr(10)+match2[1] +chr(10)+match2[2] +chr(10)+match2[3] +chr(10)+match2[4] 
        
       
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="capitulo", title=scrapedtitle , url=scrapedurl1 , thumbnail=scrapedthumbnail , fanart=scrapedfanart,  plot=scrapedplot , extra=extra , folder=True) )
    
    return itemlist

def novelasa(item):
    logger.info("[tvolucion.py] novelasa")
    
    # Descarga la p‡gina
    data = scrapertools.cachePage(item.url)
    data2 = data.replace("**","=")
    extra = item.extra
    scrapedfanart = "NO"
    
    # Extrae las entradas de la pagina seleccionada

    patron = '"url"="([^"]+)",\';.*?elenco"="([^"]+)",\';.*?productor"="([^"]+)",\';.*?anio"="([^"]+)",\';.*?programa"="([^"]+)",\';.*?programaclean"="([^"]+)"\';'
    
    #patron = '"url"="([^"]+)",\';.*?elenco"="([^"]+)",\';.*?productor"="([^"]+)\';.*?anio"="([^"]+)",\';.*?programa"="([^"]+)",\';.*?programaclean"="([^"]+)"\';'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data2)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        scrapedurl = match[0]
        scrapedtitle = match[4]
        scrapedthumbnail = ""
        scrapedplot =  match[4]+chr(10)+"ELENCO :"+match[1]+chr(10)+"PRODUCTOR :"+match[2]+chr(10)+"A„O :"+match[3]
        logger.info(scrapedtitle)
        
         
        
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="capitulona", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , fanart=scrapedfanart,  plot=scrapedplot , extra=extra , folder=True) )
    
    return itemlist

def noticias(item):
    logger.info("[tvolucion.py] noticias")
    
    # Descarga la p‡gina
    data = scrapertools.cachePage(item.url)
    extra = item.extra
    scrapedfanart = "NO"
    
    # Extrae las entradas de la pagina seleccionada
    '''<li>
		<a href="http://tvolucion.esmas.com/telenovelas/romantica/amor-bravio"><img src="http://i2.esmas.com/buttons/2012/03/01/25394/170x128.jpg" alt="Amor Brav’o"></a>
		<h3>Amor Brav’o</h3>
		<h4>2012</h4>
        </li>	
        '''
    
    patron = '<a href="http://tvolucion.esmas.com/noticieros/([^"]+)"><img src="([^"]+)" alt="([^"]+)"></a>'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        scrapedurl = "http://tvolucion.esmas.com/noticieros/"+match[0]
        scrapedtitle = match[2]
        scrapedthumbnail = match[1]
        scrapedplot = "http://tvolucion.esmas.com/noticieros/"+match[0]
        logger.info(scrapedtitle)
        
        # baja fanart
        data2 = scrapertools.cachePage(scrapedurl)
        patron2 = '<img src="([^"]+)" class="stage.*?>(.*?)</div>'
        matches2 = re.compile(patron2,re.DOTALL).findall(data2)
        for match2 in matches2:
            scrapedfanart = match2[0]
        #baja plot
        patron3 = '<div class="info" style=.*?<h3>(.*?)</h3>.*?<h4>(.*?)</h4>.*?<h5>(.*?)</h5>'
        matches3 = re.compile(patron3,re.DOTALL).findall(data2)
        for match3 in matches3:
            scrapedplot = match3[0] #+chr(10)+match2[1] +chr(10)+match2[2] +chr(10)+match2[3] +chr(10)+match2[4] 
        
        
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="capitulo", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , fanart=scrapedfanart,  plot=scrapedplot , extra=extra , folder=True) )
    
    return itemlist

def programas(item):
    logger.info("[tvolucion.py] programas")
    
    # Descarga la p‡gina
    data = scrapertools.cachePage(item.url)
    extra = item.extra
    
    
    # Extrae las entradas de la pagina seleccionada
    '''<li>
		<a href="http://tvolucion.esmas.com/telenovelas/romantica/amor-bravio"><img src="http://i2.esmas.com/buttons/2012/03/01/25394/170x128.jpg" alt="Amor Brav’o"></a>
		<h3>Amor Brav’o</h3>
		<h4>2012</h4>
        </li>	
        '''
    # PROGRAMAS DE TV
    patron = '<a href="http://tvolucion.esmas.com/programas-de-tv/([^"]+)"><img src="([^"]+)" alt="([^"]+)"></a>'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        scrapedurl = "http://tvolucion.esmas.com/programas-de-tv/"+match[0]
        scrapedtitle = match[2]
        scrapedthumbnail = match[1]
        scrapedfanart = ""
        scrapedplot = "http://tvolucion.esmas.com/programas-de-tv/"+match[0]
        logger.info(scrapedtitle)
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="capitulo", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , fanart="", plot=scrapedplot , extra=extra , folder=True) )
    
    #  TELEHIT
    patron = '<a href="http://tvolucion.esmas.com/telehit/([^"]+)"><img src="([^"]+)" alt="([^"]+)"></a>'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    #itemlist = []
    for match in matches:
        scrapedurl = "http://tvolucion.esmas.com/telehit/"+match[0]
        scrapedtitle = match[2]
        scrapedthumbnail = match[1]
        scrapedfanart = ""
        scrapedplot = "http://tvolucion.esmas.com/telehit/"+match[0]
        logger.info(scrapedtitle)
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="capitulo", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , fanart="", plot=scrapedplot , extra=extra , folder=True) )
    
    #  COMICOS
    patron = '<a href="http://tvolucion.esmas.com/comicos/([^"]+)"><img src="([^"]+)" alt="([^"]+)"></a>'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    #itemlist = []
    for match in matches:
        scrapedurl = "http://tvolucion.esmas.com/comicos/"+match[0]
        scrapedtitle = match[2]
        scrapedthumbnail = match[1]
        scrapedfanart = ""
        scrapedplot = "http://tvolucion.esmas.com/comicos/"+match[0]
        logger.info(scrapedtitle)
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="capitulo", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , fanart="", plot=scrapedplot , extra=extra , folder=True) )



    return itemlist

def capitulo(item):
    logger.info("[tvolucion.py] capitulo")
    
    # Descarga la p‡gina
    data = scrapertools.cachePage(item.url)
    print data
    urlbase = item.url
    extra = item.extra
    
    # Extrae las entradas de la pagina seleccionada
    '''<tr class="odd">
        <td><a href="http://tvolucion.esmas.com/telenovelas/drama/amores-verdaderos/200767/amores-verdaderos-capitulo-75">Amenaza de muerte</a></td>
        <td>En el capitulo 75 de Amores verdaderos, Leonardo amenaza a Beatriz, la maltrata y le asegura que si no regresa con l, la mata</td>
        <!-- <td class="right">8,572</td> -->
        <td>00:40:39</td>
        <td>14/12/12</td>
        <td class="noborder">75</td>
        </tr>
        
        '''
    # NOVELAS
    # patron = '<td><a href="http://tvolucion.esmas.com/telenovelas/([^"]+)">([^<]+)</a>.*?<td>'
    patron = '<td><a href="http://tvolucion.esmas.com/telenovelas/([^"]+)">([^<]+)</a>.*?<td>([^<]+)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td class="noborder">(.*?)</td>.*?</tr>'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        scrapedurl = "http://tvolucion.esmas.com/telenovelas/"+match[0]+"/"
        scrapedtitle = match[5]+" - "+match[1]
        scrapedthumbnail = item.thumbnail
        scrapedfanart = item.fanart
        scrapedplot = match[2]+ chr(10)+" DURACION : "+match[3]+chr(10)+" ESTRENO : "+match[4]  +chr(10)+item.fanart
        print scrapedtitle
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="video", title=scrapedtitle , url=scrapedurl , page=urlbase, thumbnail=scrapedthumbnail ,fanart=scrapedfanart,  plot=scrapedplot , extra=extra , folder=True) )
    
    # NOVELAS V2
    '''
        <ul id="cont-fila-art">
        <li class="thumb"><a href="http://tvolucion.esmas.com/telenovelas/drama/abismo-de-pasion/179216/abismo-pasion-capitulo-114/" target="_top"><img src="http://m4v.tvolucion.com/m4v/boh/abism/abism-c114/abism-c114.jpg" align="left"></a></li>
        <li class="nombrePrograma">Abismo de pasi—n</li>
        <li class="titulo-art">Cancelar el contrato</li>
        <li class="Duracion">Duracion: 00:42:12</li>
        <li class="capitulo">Capitulo: 114</li>
        <li class="pre-fecha">Fecha:&nbsp;</li>
        <li class="fecha-pub-art">&nbsp;29/06/2012</li>
        </ul>

       <R N="1"><U>http://tvolucion.esmas.com/telenovelas/drama/amores-verdaderos/200767/amores-verdaderos-capitulo-75/</U><UE>http://tvolucion.esmas.com/telenovelas/drama/amores-verdaderos/200767/amores-verdaderos-capitulo-75/</UE><T>Amenaza de muerte</T><RK>10</RK><CRAWLDATE>17 Dec 2012</CRAWLDATE><ENT_SOURCE>T2-A5AY6GP5HY2T5</ENT_SOURCE><FS NAME="date" VALUE="2012-12-17"/><S>Amenaza de muerte </S><LANG>en</LANG><HAS><L/><C SZ="1k" CID="9rajlf5d3UQJ" ENC="ISO-8859-1"/></HAS></R>
        <R N="2"><U>http://tvolucion.esmas.com/telenovelas/drama/amores-verdaderos/200431/amores-verdaderos-capitulo-73/</U><UE>http://tvolucion.esmas.com/telenovelas/drama/amores-verdaderos/200431/amores-verdaderos-capitulo-73/</UE><T>Culpa de padres</T><RK>10</RK><ENT_SOURCE>T2-A5AY6GP5HY2T5</ENT_SOURCE><FS NAME="date" VALUE="2012-12-13"/><S>Culpa de padres </S><LANG>en</LANG><HAS><L/><C SZ="1k" CID="JsPJNG5nJo8J" ENC="ISO-8859-1"/></HAS></R>
        
        <li>
		<a href="http://tvolucion.esmas.com/telenovelas/drama/amores-verdaderos/200767/amores-verdaderos-capitulo-75"><img src="http://m4v.tvolucion.com/m4v/boh/verda/b6206593f5defebda8ed2ed456a3230b/defebda8ed.jpg" /></a>
		<h3>Amores verdaderos</h3>
		<h4>Amenaza de muerte</h4>
		<h4>Duraci—n: 00:40:39</h4>
		<h4>Cap’tulo: 75</h4>
		<h4>Fecha: 14/12/12</h4>
        </li>
        
        <li>.*?<a href="([^"]+)"><img src="([^"]+)" /></a>.*?<h3>([^<]+)</h3>.*?<h4>([^<]+)</h4>.*?<h4>Duraci—n: ([^<]+)</h4>.*?<h4>Cap’tulo: ([^<]+)</h4>.*?<h4>Fecha: ([^<]+)</h4>.*?</li>
        
        0 link
        1 poster
        2 novela
        3 episodio
        4 duracion
        5 capitulo
        6 fecha
        
        '''
    #patron = '<ul id="cont-fila-art">.*?<li class="thumb"><a href="http://tvolucion.esmas.com/telenovelas/([^"]+)" target="_top"><img src="([^"]+)" align="left"></a></li>.*?<li class="nombrePrograma">(.*?)</li>.*?<li class="titulo-art">(.*?)</li>.*?<li class="Duracion">Duracion: (.*?)</li>.*?<li class="capitulo">Capitulo: (.*?)</li>.*?<li class="pre-fecha">Fecha:&nbsp;</li>.*?<li class="fecha-pub-art">&nbsp;(.*?)</li>.*?</ul>'
    #patron = '<li>.*?<a href="([^"]+)"><img src="([^"]+)" /></a>.*?<h3>(.*?)</h3>.*?<h4>(.*?)</h4>.*?<h4>Duraci—n: (.*?)</h4>.*?<h4>Cap’tulo: (.*?)</h4>.*?<h4>Fecha: (.*?)</h4>.*?</li>'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    patron = '<R N=".*?"><U>([^<]+)</U><UE>.*?capitulo-(.*?)/</UE><T>([^<]+)</T><RK>.*?</RK>.*?<ENT_SOURCE>.*?</ENT_SOURCE><FS NAME="date" VALUE="([^"]+)"/><S>(.*?)</S><LANG>.*?</LANG><HAS><L/><C SZ=".*?" CID=".*?" ENC=".*?"/></HAS></R>'
    print "intenta obtener patron 2"
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        scrapedurl = match[0] #"http://tvolucion.esmas.com/telenovelas/"+match[0]+"/"
        print scrapedurl
        scrapedtitle = match[1]+" - "+match[2]
        scrapedthumbnail = ""#match[1]
        scrapedfanart = item.fanart
        scrapedplot = ""#match[3]+ chr(10)+" DURACION : "+match[4]+chr(10)+" ESTRENO : "+match[6]  +chr(10)+match[0]
        
        
        logger.info(scrapedtitle)
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="video", title=scrapedtitle , url=scrapedurl , page=urlbase, thumbnail=scrapedthumbnail ,fanart=scrapedfanart,  plot=scrapedplot , extra=extra , folder=True) )
    # NOTICIAS
    # patron = '<td><a href="http://tvolucion.esmas.com/telenovelas/([^"]+)">([^<]+)</a>.*?<td>'
    patron = '<td><a href="http://tvolucion.esmas.com/noticieros/([^"]+)">([^<]+)</a>.*?<td>([^<]+)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td class="noborder">(.*?)</td>'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
#itemlist = []
    for match in matches:
        scrapedurl = "http://tvolucion.esmas.com/noticieros/"+match[0]
        scrapedtitle = match[5]+" - "+match[1]
        scrapedthumbnail = item.thumbnail
        scrapedfanart = item.fanart
        scrapedplot = match[2]+ chr(10)+" DURACION : "+match[3]+chr(10)+" ESTRENO : "+match[4]  +chr(10)+"http://tvolucion.esmas.com/noticieros/"+match[0]
        
        
        logger.info(scrapedtitle)
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="video", title=scrapedtitle , url=scrapedurl ,  page=urlbase, thumbnail=scrapedthumbnail ,fanart=scrapedfanart,  plot=scrapedplot , extra=extra , folder=True) )

    # COMICOS
    # patron = '<td><a href="http://tvolucion.esmas.com/telenovelas/([^"]+)">([^<]+)</a>.*?<td>'
    patron = '<td><a href="http://tvolucion.esmas.com/comicos/([^"]+)">([^<]+)</a>.*?<td>([^<]+)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td class="noborder">(.*?)</td>'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    #itemlist = []
    for match in matches:
        scrapedurl = "http://tvolucion.esmas.com/comicos/"+match[0]+"/"
        scrapedtitle = match[1]
        scrapedthumbnail = item.thumbnail
        scrapedplot = match[2]+ chr(10)+" DURACION : "+match[3]+chr(10)+" ESTRENO : "+match[4]  +chr(10)+"http://tvolucion.esmas.com/comicos/"+match[0]+"/"
        scrapedfanart = item.fanart
        logger.info(scrapedtitle)
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="video", title=scrapedtitle , url=scrapedurl , page=urlbase, thumbnail=scrapedthumbnail ,fanart=scrapedfanart,  plot=scrapedplot , extra=extra , folder=True) )    
    
    # PROGRAMAS TV
    # patron = '<td><a href="http://tvolucion.esmas.com/telenovelas/([^"]+)">([^<]+)</a>.*?<td>'
    patron = '<td><a href="http://tvolucion.esmas.com/programas-de-tv/([^"]+)">([^<]+)</a>.*?<td>([^<]+)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td class="noborder">(.*?)</td>'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    #itemlist = []
    for match in matches:
        scrapedurl = "http://tvolucion.esmas.com/programas-de-tv/"+match[0]+"/"
        scrapedtitle = match[5]+" - "+match[1]
        scrapedthumbnail = item.thumbnail
        scrapedplot = match[2]+ chr(10)+" DURACION : "+match[3]+chr(10)+" ESTRENO : "+match[4] 
        scrapedfanart = item.fanart
        logger.info(scrapedtitle)
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="video", title=scrapedtitle , url=scrapedurl , page=urlbase, thumbnail=scrapedthumbnail ,fanart=scrapedfanart,  plot=scrapedplot , extra=extra , folder=True) )

    # PROGRAMAS - TELEHIT
    # patron = '<td><a href="http://tvolucion.esmas.com/telenovelas/([^"]+)">([^<]+)</a>.*?<td>'
    patron = '<td><a href="http://tvolucion.esmas.com/telehit/([^"]+)">([^<]+)</a>.*?<td>([^<]+)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td class="noborder">(.*?)</td>'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    #itemlist = []
    for match in matches:
        scrapedurl = "http://tvolucion.esmas.com/telehit/"+match[0]+"/"
        scrapedtitle = match[5]+" - "+match[1]
        scrapedthumbnail = item.thumbnail
        scrapedplot = match[2]+ chr(10)+" DURACION : "+match[3]+chr(10)+" ESTRENO : "+match[4] 
        scrapedfanart = item.fanart
        logger.info(scrapedtitle)
                # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="video", title=scrapedtitle , url=scrapedurl , page=urlbase, thumbnail=scrapedthumbnail ,fanart=scrapedfanart,  plot=scrapedplot , extra=extra , folder=True) )  
    
    # PROGRAMAS - EL CHAVO
    patron = 'var playlistURL_dos = \'(.*?)&callback=.*?start-index=(.*?)&max-results=50'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    number = item.extra
    print number
    flag = number.isdigit()
    print flag
    if flag :
        number = int(number) 
    else :
        number = 1
    print number
    if DEBUG: scrapertools.printMatches(matches)
    #baja json
    for match in matches:
        scrapedurl = match[0]+"&start-index="+str(number)+"&max-results=50&orderby=published"
        scrapedtitle = "test"
        scrapedthumbnail = ""
        scrapedplot = match[0]
        scrapedfanart = ""
        number = number +50
        print number
        print scrapedurl
        # baja caps
        '''
           "title":{"$t":"Juguetes de papel"},"content":{"type":"application/x-shockwave-flash","src":"http://www.youtube.com/v/0Tl1Okg_h48?version=3&f=playlists&app=youtube_gdata"},"link":[{"rel":"alternate","type":"text/html","href":"http://www.youtube.com/watch?v=0Tl1Okg_h48&feature=youtube_gdata"}, 
        '''
        data2 = scrapertools.cachePage(scrapedurl)
        data2 = data2.replace("$","")
        patron2 = '"title":{"t":"([^"]+)"},"content":{"type":"application/x-shockwave-flash","src":"(.*?)version=3&f=playlists&app=youtube_gdata"},"link.*?"alternate","type":"text/html","href":"(.*?)"}.*?"mediadescription":{"t":"([^"]+)","type":"plain"},"mediakeywords":'
        matches2 = re.compile(patron2,re.DOTALL).findall(data2)
        count = 1
        for match2 in matches2:
            scrapedtitle = match2[0]
            scrapedurl = match2[2]
            #scrapedurl = match2[1][:match2[1].find("?")]
            #scrapedurl = scrapedurl.replace("http://www.youtube.com/v/","http://www.youtube.com/watch?v=")
            scrapedplot = match2[3]
            id = match2[1].replace("http://www.youtube.com/v/","")
            id = id[:id.find("?")]
            print str(count) + " " +id
            scrapedthumbnail = "http://i.ytimg.com/vi/"+id+"/hqdefault.jpg"
            count = count +1
            # A–ade al listado
            itemlist.append( Item(channel=__channel__, action="play", server="youtube", title=scrapedtitle , url=scrapedurl , page=urlbase, thumbnail=scrapedthumbnail ,fanart=scrapedfanart,  plot=scrapedplot , extra=extra , folder=False) )  

        # A–ade al listado
        print count
        if count > 35:
            itemlist.append( Item(channel=__channel__, action="capitulo", title="CAPITULOS ANTERIORES >>" , url=item.url , page=urlbase, thumbnail="" ,fanart=scrapedfanart,  plot="Ver capitulos anteriores." , extra=str(number) , folder=True) ) 

    # KIDS -CINE Y TV

    patron = '<td><a href="([^"]+)">([^<]+)</a>.*?<td>([^<]+)</td>.*?<td>([^<]+)</td>.*?<td>([^<]+)</td>'
    #patron = 'href="([^"]+)"><img src="([^"]+)" /></a>.*?<h4>([^<]+)</h4>.*?<h4>([^<]+)</h4>.*?<h4>([^<]+)</h4>.*?<h4>([^<]+)</h4>'

    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    #itemlist = []
    for match in matches:
        scrapedurl = match[0]
        scrapedtitle = match[1]
        scrapedthumbnail = ""
        scrapedplot = match[2]+ chr(10)+" DURACION : "+match[3]+chr(10)+" ESTRENO : "+match[4] 
        scrapedfanart = ""
        
        # baja fanart
        data2 = scrapertools.cachePage(scrapedurl)
        '''
            videoImgFrame='http://m4v.tvolucion.com/m4v/cus/trail/trail-20120223erahielo4/trail-20120223erahielo4.jpg';
        '''
        print "bajando imagen para video "+match[1]
        patron2 = 'videoUrlQvt = \'(.*?)\';.*?videoImgFrame=\'(.*?)\';.*?'
        matches2 = re.compile(patron2,re.DOTALL).findall(data2)
        for match2 in matches2:
            scrapedthumbnail = match2[1]
            scrapedurl2  = match2[0]
        
        logger.info(scrapedtitle)
    
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="video", title=scrapedtitle , url=scrapedurl , page=urlbase, thumbnail=scrapedthumbnail ,fanart=scrapedfanart,  plot=scrapedplot , extra=extra , folder=True) )

 

    return itemlist

def playYoutube(item):
    logger.info("[tvolucion.py] playYoutube")
    
    itemlist = []
    
    # Extrae el ID
    id = youtube.Extract_id(item.url)
    logger.info("[tvolucion.py] id="+id)
    
    # Descarga la p‡gina
    data = scrapertools.cache_page(item.url)
    
    # Obtiene la URL
    url = youtube.geturls(id,data)
    
    itemlist.append( Item(channel=CHANNELNAME, title=item.title , action="play" , server="Directo", url=url, thumbnail=item.thumbnail , folder=False) )
    
    return itemlist

def capitulona(item):
    logger.info("[tvolucion.py] capitulona")
    
    # Descarga la p‡gina
    data = scrapertools.cachePage(item.url)
    urlbase = item.url
    extra = item.extra
    
    # Extrae las entradas de la pagina seleccionada
    '''<td><a href="http://tvolucion.esmas.com/telenovelas/romantica/amor-bravio/175807/amor-bravio-capitulo-67">Regresa el padre de Ximena</a></td>
        <td>En el capitulo 67 de Amor brav’o, Francisco se presenta con Dionisio para cobrar la herencia de Daniel y es reconocido como el pap‡ de Ximena</td>
        <!-- <td class="right">8,572</td> -->
        <td>00:43:18</td>
        <td>05/06/12</td>
        <td class="noborder">67</td>
        
        '''
    # NOVELAS
    # patron = '<td><a href="http://tvolucion.esmas.com/telenovelas/([^"]+)">([^<]+)</a>.*?<td>'
    patron = '<td><a href="http://tvolucion.esmas.com/telenovelas/([^"]+)">([^<]+)</a>.*?<td>([^<]+)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td class="noborder">(.*?)</td>'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        scrapedurl = "http://tvolucion.esmas.com/telenovelas/"+match[0]+"/"
        scrapedtitle = match[5]+" - "+match[1]
        scrapedthumbnail = item.thumbnail
        scrapedfanart = item.fanart
        scrapedplot = match[2]+ chr(10)+" DURACION : "+match[3]+chr(10)+" ESTRENO : "+match[4]  +chr(10)+scrapedurl
        
        
        logger.info(scrapedtitle)
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="videona", title=scrapedtitle , url=scrapedurl , page=urlbase, thumbnail=scrapedthumbnail ,fanart=scrapedfanart,  plot=scrapedplot , extra=extra , folder=True) )
      
    return itemlist

def videona(item):
    logger.info("[tvolucion.py] videona")
    
    # Descarga la p‡gina
    data = scrapertools.cachePage(item.url)
    extra = item.extra
    
    
    '''
        videoUrlQvt = 'http://m4v.tvolucion.com/m4v/boh/dadmi/dadmi-20111031derecho/dadmi-20111031derecho-480.mp4';
        id: "8736919-e95e4cda-986a-4590-ae1f-6aa1e797de75",	cat: "2012/06/08",   profile: "bca",    gbs : 
        
        id: "133275", cat: "esmas", profile: "hls2", gbs: "716ee5cf447289f814a8ef5f9ad86bb5"
        http://publish20.cdn.movenetworks.com/cms/publish/vod/vodclip/esmas/133275.qvt
        http://media.esmas.com/criticalmedia/files/2012/06/08/8736919-e95e4cda-986a-4590-ae1f-6aa1e797de75.mp4
        scrapedurl = "http://publish20.cdn.movenetworks.com/cms/publish/vod/vodclip/"+match[2]+"/"+match[1]+".qvt"
        patron = 'thumbnail: "([^"]+)".*?id: "([^"]+)".*?cat: "([^"]+)",.*?profile: "([^"]+)",.*?gbs: "([^"]+)",.*?extension = \'(.*?)\';'
        scrapedurl = "http://media.esmas.com/criticalmedia/files/"+match[2]+"/"+match[1]+".mp4"
        http://media.esmas.com/criticalmedia/files/2011/07/09/4297022-45b437e6-9db3-4425-a2cc-448cdde97c69.mp4
        
        http://media.esmas.com/criticalmedia/assets/2713950-b790cc30-8ac1-48ff-95e3-37bc18b4db39.mp4
        
        http://apps.tvolucion.com/m3u8/tln/t1-c143-teres/t1-c143-teres.m3u8
        '''
    #OTROS (WEB NORMAL)   
    patron = 'videoUrlQvt = \'(.*?)\';.*?thumbnail: "([^"]+)".*?id: "([^"]+)".*?cat: "([^"]+)",.*?profile: "([^"]+)",.*?gbs: "([^"]+)",.*?extension = \'(.*?)\';'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        plus = ""
        extension = match[6][2:]
        flag = extension.isdigit()
        scrapedurl = match[0]
        find = scrapedurl.find("-480.mp4")
        if find >= 0 :
            scrapedurl = scrapedurl.replace("-480.mp4","/")+match[2]
            scrapedurl = scrapedurl.replace("-480",".m3u8")
            scrapedurl = scrapedurl.replace("m4v.","apps.")
            scrapedurl = scrapedurl.replace("/m4v/","/m3u8/")
            print "1 " + scrapedurl
        else :
            scrapedurl = match[0]
            print "1 " + scrapedurl
        #scrapedurl = scrapedurl.replace("http://","rtmp://")
        #scrapedurlhd = scrapedurlhd.replace("-480.mp4","-,15,48,60,0.mp4.csmil/bitrate=2")
        scrapedtitle =  item.title
        scrapedthumbnail = match[1]
        scrapedfanart = item.fanart
        scrapedplot = item.plot
        logger.info(scrapedtitle)
        print scrapedurl
        # A–ade al listado
        
        # CALIDAD MEDIA
        if flag :
            if (float(extension) != 4) :
                ends = match[2]
                ends = ends[ends.find("/"):]
                scrapedurl = "http://apps.tvolucion.com/m4v/"+match[3]+"/"+match[2]+"/"+ends+"-600.mp4"
            scrapedplot=scrapedplot+chr(10)+scrapedurl +chr(10)+extension+chr(10)+match[0]
            itemlist.append( Item(channel=__channel__, action="play", title=scrapedtitle+" (Calidad: Media)" , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=False) )
        else :
            scrapedplot=scrapedplot+chr(10)+scrapedurl +chr(10)+extension+chr(10)+match[0]
            
            itemlist.append( Item(channel=__channel__, action="capitulo", title="VIDEO NO COMPATIBLE" , url=item.page,  thumbnail=scrapedthumbnail , plot="Video formato QVT, no compatible con XBMC" , extra=extra , folder=False) )       
    
    
    
    return itemlist


def video(item):
    logger.info("[tvolucion.py] video")
    
    # Descarga la p‡gina
    data = scrapertools.cachePage(item.url)
    extra = item.extra
    print "entra a video"
    # Extrae las entradas de la pagina seleccionada
    '''<video width="294" height="165" controls autoplay="autoplay" poster="http://m4v.tvolucion.com/m4v/boh/abism/abism-c092/abism-c092.jpg" style="margin: 0pt 13px;">
        <source src="http://apps.tvolucion.com/m4v/boh/abism/abism-c092/abism-c092-150.mp4" type="video/mp4; codecs='avc1,mp4a'" />
        </video>
        
        http://m4vhd.tvolucion.com/m4v/boh/abism/abism-c001/abism-c001-,15,48,60,0.mp4.csmil/bitrate=2
        
        
        <video width="294" height="165" controls autoplay="autoplay" poster="http://media.esmas.com/criticalmedia/files/2012/06/07/8721239-c7c8bd61-a196-471b-a98f-789b0468c458.jpg" style="margin: 0pt 13px;">
        <source src="http://apps.esmas.com/criticalmedia/files/2012/06/07/8721242-9043291a-ab74-4c1e-bdde-326c425e341d.mp4" type="video/mp4; codecs='avc1,mp4a'" />
        </video>
        
        
        videoUrlQvt = 'http://media.esmas.com/criticalmedia/files/2012/06/07/8721806-07abc298-eac0-4050-abfa-8199bb0ee2e9.mp4';	
        http://apps.esmas.com/criticalmedia/files/2012/06/07/8721242-9043291a-ab74-4c1e-bdde-326c425e341d.mp4
        
        // alert('id: "8721806-07abc298-eac0-4050-abfa-8199bb0ee2e9",	cat: "2012/06/07",   profile: "bca",    otro : ');
        
        '''
    #NOVELAS (WEB MOVIL)   
    print "INTENRTA MOVIL"
    patron = '<video id="video1" width="294" height="165" controls  poster="([^"]+)" style=.*?<source src="([^"]+)" type="([^"]+)" />'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        print "encontro movil"
        scrapedurl = match[1]
        scrapedurl = scrapedurl.replace("-150.mp4","-480.mp4")
        #scrapedurl = scrapedurl.replace("http://","rtmp://")
        scrapedurlhd = scrapedurl.replace("apps.","apps.")
        scrapedurlhd = scrapedurlhd.replace("-480.mp4","-600.mp4")
        
        scrapedtitle =  item.title
        scrapedthumbnail = match[0]
        scrapedfanart = item.fanart
        scrapedplot = item.plot +chr(10)+scrapedurl +chr(10)+scrapedurlhd
        logger.info(scrapedtitle)
        
        # A–ade al listado
        
        # CALIDAD MEDIA
        itemlist.append( Item(channel=__channel__, action="play", title=scrapedtitle+" (Calidad: Media)" , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) ) 
        # CALIDAD HD
        itemlist.append( Item(channel=__channel__, action="play", title=scrapedtitle+" (Calidad: HD)" , url=scrapedurlhd , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) )    
    
    '''
        videoUrlQvt = 'http://m4v.tvolucion.com/m4v/boh/dadmi/dadmi-20111031derecho/dadmi-20111031derecho-480.mp4';
        id: "8736919-e95e4cda-986a-4590-ae1f-6aa1e797de75",	cat: "2012/06/08",   profile: "bca",    gbs : 
        
        id: "133275", cat: "esmas", profile: "hls2", gbs: "716ee5cf447289f814a8ef5f9ad86bb5"
        http://publish20.cdn.movenetworks.com/cms/publish/vod/vodclip/esmas/133275.qvt
        http://media.esmas.com/criticalmedia/files/2012/06/08/8736919-e95e4cda-986a-4590-ae1f-6aa1e797de75.mp4
        scrapedurl = "http://publish20.cdn.movenetworks.com/cms/publish/vod/vodclip/"+match[2]+"/"+match[1]+".qvt"
        patron = 'thumbnail: "([^"]+)".*?id: "([^"]+)".*?cat: "([^"]+)",.*?profile: "([^"]+)",.*?gbs: "([^"]+)",.*?extension = \'(.*?)\';'
        scrapedurl = "http://media.esmas.com/criticalmedia/files/"+match[2]+"/"+match[1]+".mp4"
        '''
    print "INTENTA WEB"
    #OTROS (WEB NORMAL)   
    patron = 'videoUrlQvt = \'(.*?)\';.*?thumbnail: "([^"]+)".*?id: "([^"]+)".*?cat: "([^"]+)",.*?profile: "([^"]+)",.*?gbs: "([^"]+)",.*?extension = \'(.*?)\';'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    if DEBUG: scrapertools.printMatches(matches)
    #itemlist = []
    for match in matches:
        print "encontro web"
        plus = ""
        extension = match[6][2:]
        flag = extension.isdigit()
        print flag
        scrapedurl = match[0]
        #"http://media.esmas.com/criticalmedia/files/"+match[3]+"/"+match[2]+".mp4"
        scrapedurl = scrapedurl.replace("-480.mp4","-600.mp4")
        scrapedurl = scrapedurl.replace("m4v.","apps.")
        if "?" in scrapedurl:
            scrapedurl = scrapedurl[:scrapedurl.find("?")]
        #scrapedurl = scrapedurl.replace("http://","rtmp://")
        #scrapedurlhd = scrapedurlhd.replace("-480.mp4","-,15,48,60,0.mp4.csmil/bitrate=2")
        scrapedtitle =  item.title
        scrapedthumbnail = match[1]
        scrapedfanart = item.fanart
        scrapedplot = item.plot
        logger.info(scrapedtitle)
        print str(scrapedurl)
        # A–ade al listado
        
        # CALIDAD MEDIA
        if flag :
            print  "entra a la bandera"
            if (float(extension) != 4) :
                print "formato no es mp4"
                ismp4 = scrapedurl.find(".mp4")
                if ismp4 >=1:
                    print "si es mp4, se queda el url original"
                else:
                    ends = match[2]
                    isf1 = ends.find("/")
                    if isf1 >=1:
                        print isf1
                        ends = ends[ends.find("/"):]
                        scrapedurl = "http://apps.tvolucion.com/m4v/"+match[3]+"/"+match[2]+"/"+ends+"-600.mp4"
                    else:
                        scrapedurl = match[1].replace(".jpg","-600.mp4")
                        scrapedurl = scrapedurl.replace("m4v.","apps.")
            scrapedplot=scrapedplot+chr(10)+scrapedurl +chr(10)+extension+chr(10)+match[0]
            itemlist.append( Item(channel=__channel__, action="play", title=scrapedtitle+" (Calidad: Media)" , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) )
        else :
            if scrapedurl.find(".mp4"):
                 itemlist.append( Item(channel=__channel__, action="play", title=scrapedtitle+" (Calidad: Web)" , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) )
            else:
                 print "no es mp, probablemente es formato anterior QVT"
                 scrapedplot=scrapedplot+chr(10)+scrapedurl +chr(10)+extension+chr(10)+match[0]
                 itemlist.append( Item(channel=__channel__, action="capitulo", title="VIDEO NO COMPATIBLE" , url=item.page,  thumbnail=scrapedthumbnail , plot="Video formato QVT, no compatible con XBMC" , extra=extra , folder=True) )
    
    
    return itemlist

def tv(item):
    logger.info("[tvolucion.py] tv")
    
    # Descarga la p‡gina
    data = scrapertools.cachePage(item.url)
    extra = item.extra
    
    # Extrae las entradas de la pagina seleccionada
    '''<video width="294" height="165" controls autoplay="autoplay" poster="http://m4v.tvolucion.com/m4v/boh/abism/abism-c092/abism-c092.jpg" style="margin: 0pt 13px;">
        <source src="http://apps.tvolucion.com/m4v/boh/abism/abism-c092/abism-c092-150.mp4" type="video/mp4; codecs='avc1,mp4a'" />
        </video>
        http://apps.tvolucion.com/m4v/boh/teresa/teresa-capitulo-148/t1.148-teres-480.mp4
        http://apps.tvolucion.com/m4v/tln/t1.148-teres-480.mp4
        
        http://m4vhd.tvolucion.com/m4v/boh/abism/abism-c001/abism-c001-,15,48,60,0.mp4.csmil/bitrate=2
        rtmp://bright.tvolucion.com/ondemand/files/m4v/mp4:tln/t1-c101-desti/t1-c101-desti-150.mp4
        '''
    
    patron = 'flashvars="&streamer=(.*?).flv&autostart=(.*?).*?/></embed>'
    # patron += 'href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        scrapedurl = "rtmp://176.31.231.57/edge playpath=to8ykizy8es8pl5 swfUrl=http://cdn.static.ilive.to/jwplayer/player_new.swf pageUrl=http://www.ilive.to/view/1598/dansertv_2 timeout=60"
        
        scrapedtitle = "CANAL DE LAS ESTRELLAS"
        scrapedthumbnail = "http://3.bp.blogspot.com/-DI-1Ceh_4Tk/T0m0XVZ9KqI/AAAAAAAABKk/EIdylQgWr0w/s1600/Canal-Estrellas-En_Vivo.jpg"
        scrapedplot = "Es el canal familiar de Televisa, promueve los valores, las tradiciones y el respeto. Es l’der en la televisi—n mexicana y l’der de habla hispana en el mundo, transmite diariamente a Estados Unidos, Canad‡, Centro y SudamŽrica, Europa y Ocean’a. Su programaci—n incluye telenovelas, noticieros, espect‡culos, deportes, unitarios, etc."
        logger.info(scrapedtitle)
        
        # A–ade al listado
        
        # CALIDAD MEDIA
        itemlist.append( Item(channel=__channel__, action="play", title=scrapedtitle+" (Calidad: Media)" , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=False) )
                  
    
    # rtmp://cp77659.live.edgefcs.net:1935/live/1_pvpj8n23_1@60491
        scrapedurl = "rtmp://c81.webcaston.com/live/channel/telerisa playpath:telerisa swfUrl=http://www.webcaston.com/player/player.swf pageUrl=http://www.webcaston.com/telerisa"
                
        scrapedtitle = "CANAL 13"
        scrapedthumbnail = "http://3.bp.blogspot.com/-DI-1Ceh_4Tk/T0m0XVZ9KqI/AAAAAAAABKk/EIdylQgWr0w/s1600/Canal-Estrellas-En_Vivo.jpg"
        scrapedplot = "Es el canal familiar de Televisa, promueve los valores, las tradiciones y el respeto. Es l’der en la televisi—n mexicana y l’der de habla hispana en el mundo, transmite diariamente a Estados Unidos, Canad‡, Centro y SudamŽrica, Europa y Ocean’a. Su programaci—n incluye telenovelas, noticieros, espect‡culos, deportes, unitarios, etc."
        logger.info(scrapedtitle)
                
        # A–ade al listado
                
        # CALIDAD MEDIA
    #     itemlist.append( Item(channel=__channel__, action="play", title=scrapedtitle+" (Calidad: Media)" , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=extra , folder=True) )    
    return itemlist

#    patron = 'flashvars="&streamer=(.*?).flv&autostart=(.*?).*?/></embed>'
#        scrapedurl = "rtmp://live.ilive.to/redirect&file=to8ykizy8es8pl5.flv"
#        scrapedtitle =  match[0]
        # scrapedthumbnail = ""
        #        scrapedplot = "rtmp://live.ilive.to/redirect&file=to8ykizy8es8pl5.flv"
        #        logger.info(scrapedtitle)
        
def teresa(item):
    logger.info("[tvolucion.py] teresa")
    
    # Descarga la p‡gina
    data = scrapertools.cachePage(item.url)
    extra = item.extra
    scrapedfanart = "NO"
    
    # Extrae las entradas de la pagina seleccionada
    
    patron = '<td><a href="(.*?)">(.*?)</a></td>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        scrapedurl = match[0]
        scrapedtitle = match[1]
        scrapedthumbnail = ""
        scrapedplot =  match[1]
        logger.info(scrapedtitle)
        
        
        
        
        # A–ade al listado
        itemlist.append( Item(channel=__channel__, action="play", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , fanart=scrapedfanart,  plot=scrapedplot , extra=extra , folder=True) )
    
    return itemlist        


def search(item,texto):
    logger.info("[tvolucion.py] search")
    itemlist = []
    
    texto = texto.replace(" ","+")
    try:
        # Series
        item.url="http://www.peliculasaudiolatino.com/result.php?q=%s&type=search&x=0&y=0"
        item.url = item.url % texto
        item.extra = ""
        itemlist.extend(listado2(item))
        itemlist = sorted(itemlist, key=lambda Item: Item.title) 
        
        return itemlist
    
    # Se captura la excepci—n, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():

    # Todas las opciones tienen que tener algo
    items = mainlist(Item())
    series_items = novelasr(items[2])
    for serie_item in series_items:
        exec "itemlist="+serie_item.action+"(serie_item)"
    
        if len(itemlist)>0:
            return True

    return True
