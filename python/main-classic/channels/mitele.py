# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para mitele
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# Por Truenon y Jesus, modificada por Boludiko
# v11
#------------------------------------------------------------
import urlparse,urllib2,urllib,re,sys

from core import logger
from core import config
from core import scrapertools
from core import aes          
from core.item import Item
from servers import servertools
from StringIO import StringIO
import gzip
import xml.parsers.expat
from core import jsontools

__channel__ = "mitele"
__category__ = "S,F,A"
__type__ = "generic"
__title__ = "Mi tele"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[seriesyonkis.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Series"    , action="series"  , category="series"    , thumbnail = "" , url="http://www.mitele.es/series-online/"))
    itemlist.append( Item(channel=__channel__, title="Programas" , action="series"  , category="programas" , thumbnail = "" , url="http://www.mitele.es/programas-tv/"))
    itemlist.append( Item(channel=__channel__, title="Moto GP" , action="series"  , category="programas" , thumbnail = "" , url="http://www.mitele.es/motogp/"))
    itemlist.append( Item(channel=__channel__, title="TV Movies" , action="series"  , category="series"    , thumbnail = "" , url="http://www.mitele.es/tv-movies/"))
    itemlist.append( Item(channel=__channel__, title="V.O."      , action="series"  , thumbnail = "" , url="http://www.mitele.es/mitele-vo/"))
    #itemlist.append( Item(channel=__channel__, title="Directo"   , action="directo" , thumbnail = "" , url="http://www.mitele.es/directo/"))
    return itemlist

def series(item):
    logger.info("[mitele.py] series")
    itemlist = []
    
    # Extrae los programas
    if item.extra=="":
        item.extra="1"

    headers=[]
    headers.append(["Content-Type","application/x-www-form-urlencoded; charset=UTF-8"])
    headers.append(["Referer",item.url])
    headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:10.0) Gecko/20100101 Firefox/10.0"])
    headers.append(["X-Requested-With","XMLHttpRequest"])

    data = scrapertools.cache_page(item.url , post="pag="+item.extra, headers=headers)
    logger.info("data="+data)
    patron  = '<li.*?</li>'
    matches = re.findall(patron,data,re.DOTALL)
    #if DEBUG: scrapertools.printMatches(matches)
    
    for subdata in matches:
        patron  = 'href="([^"]+)".*?title="([^"]+)".*?src="([^"]+)"'
        matches2 = re.findall(patron,subdata,re.DOTALL)
        for match in matches2:
            scrapedurl = "http://www.mitele.es" + match[0]
            scrapedtitle = match[1]
            scrapedthumbnail = match[2]
            scrapedplot = ""
            itemlist.append( Item(channel=__channel__, action="temporadas" , title=scrapedtitle,  fulltitle=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, show=scrapedtitle, category=item.category))

    if len(itemlist)==0:
        return []

    if item.extra=="":
        item.extra="2"
    else:
        item.extra = str(int(item.extra)+1)
    itemlist.extend( series(item) )

    return itemlist

def temporadas(item):
    logger.info("[mitele.py] Temporadas")

    # Extrae las temporadas
    data = scrapertools.cachePage(item.url)
    logger.info("data="+data)
    patron = 'temporadasBrowser\({\s+temporadas(.*?)\)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    data_json = '{"temporadas"'+matches[0]
    temporadas_json = jsontools.load_json(data_json)
    if temporadas_json == None : temporadas_json = []

    itemlist = []
    for temporada in temporadas_json['temporadas']:
        scrapedurl = "http://www.mitele.es/temporadasbrowser/getCapitulos/"+temporada['ID']+"/"
        scrapedtitle = temporada['post_title']
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=item.channel , action="capitulos"   , title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail, plot=scrapedplot, category=item.category, show=item.show ))
    
    return itemlist

def capitulos(item):
    logger.info("[mitele.py] Capitulos")

    if item.extra=="":
        item.extra="1"

    data = scrapertools.cachePage(item.url+"/"+item.extra)
    capitulos_json = jsontools.load_json(data)
    if capitulos_json == None : capitulos_json = []

    itemlist = []
    for capitulo in capitulos_json['episodes']:

        if item.title.startswith("Temporada "):
            numero_temporada = item.title[10:]
        else:
            numero_temporada = ""

        if capitulo['post_title'].startswith("Capítulo "):
            numero_episodio = capitulo['post_title'][10:]
        elif capitulo['post_title'].startswith("Captítulo "):
            numero_episodio = capitulo['post_title'][11:]
        elif capitulo['post_title'].startswith("Programa "):
            numero_episodio = capitulo['post_title'][9:]
        else:
            numero_episodio = ""

        if len(numero_episodio)==1:
            numero_episodio = "0"+numero_episodio
        
        if capitulo['post_subtitle'] is None:
            titulo_episodio = ""
        else:
            titulo_episodio = capitulo['post_subtitle']

        if numero_temporada!="" and numero_episodio!="":
            scrapedtitle = numero_temporada + "x" + numero_episodio+" "+titulo_episodio
        else:
            scrapedtitle = capitulo['post_title']+": "+titulo_episodio

        scrapedurl = "http://www.mitele.es"+capitulo['url'].replace("\\","")
        scrapedthumbnail = capitulo['image'] #.replace("\\","")
        scrapedplot = capitulo['post_content'].replace("<!--more-->","")
        scrapedplot = scrapertools.htmlclean(scrapedplot)

        itemlist.append( Item(channel=item.channel, action="play", server="mitele", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, category=item.category, show=item.show, folder=False ))
    
    if capitulos_json['hasNext']:
        item.extra = str(int(item.extra)+1)
        itemlist.extend( capitulos(item) )
    
    return itemlist

def capitulo(item):
    logger.info("[mitele.py] Capitulo")

    xml = getXML(item.url)
    
    data = scrapertools.cachePage(xml)
    patron = '<link start="(.*?)" end="(.*?)">(.*?)</link>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    id="XX"
    startTime = "0"
    endTime = "0"
    rtmp = False
    
    for match in matches:
        startTime = match[0]
        endTime = match[1]
        id = match[2]
        logger.info("Datos xml = "+startTime+";"+endTime+";"+id)
        
    if(id == "XX"):
        from xml.dom import minidom
        dom1 = minidom.parseString(data)
        id = dom1.getElementsByTagName("url")[1].firstChild.data            
        rtmp = True
        logger.info("Datos xml = "+startTime+";"+endTime+";"+id)

    try: 
        #TOKEN 2
        ciphertext = getciphertext(id, startTime, endTime)
        data = getvideo(id, ciphertext, 2)
        if(data<>""):
            if rtmp :
                return playrtmptoken2(item,data)
            else:
                return playvideo(item,data)
        #TOKEN 3
        ciphertext = getciphertext(id, startTime, endTime)
        data = getvideo(id, ciphertext, 3)
        if(data<>""):
            if rtmp :
                return playrtmptoken3(item,data)
            else:
                return playvideo(item,data) 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
    return itemlist


def playdirecto(item):
    itemlist = []
    try:
        startTime = "0"
        endTime = "0"
        xml = getXML(item.url)
        data = scrapertools.cachePage(xml)
        
        patron = '<link start="(.*?)" end="(.*?)">(.*?)</link>'
        matches = re.compile(patron,re.DOTALL).findall(data)
        from xml.dom import minidom
        dom1 = minidom.parseString(data)
        id = dom1.getElementsByTagName("url")[1].firstChild.data        
        logger.info("Datos xml = "+startTime+";"+endTime+";"+id)
        
        #TOKEN 2
        ciphertext = getciphertext(id, startTime, endTime)
        data = getrtmp(id,ciphertext, 2)
        if(data<>""):
            return playrtmptoken2(item,data)
        #TOKEN 3
        ciphertext = getciphertext(id, startTime, endTime)
        data = getrtmp(id,ciphertext, 3)
        if(data<>""):
            return playrtmptoken3(item,data)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
            
    return itemlist



def directo (item):
    logger.info("[mitele.py] directo")
    itemlist = []
    data = scrapertools.cachePage(item.url)
    
    # Extrae los programas
    patron  = '<ul id="canales">(.*?)</ul>'
    matches = re.findall(patron,data,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    if len(matches)>0:
        subdata = matches[0]
    else:
        return itemlist
    
    patron  = '<li.*?</li>'
    matches = re.findall(patron,subdata,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)
    
    if len(matches)>0:
        for subdata in matches:
            patron  = 'href="([^"]+)".*?src="([^"]+)"'
            matches2 = re.findall(patron,subdata,re.DOTALL)
            for match in matches2:
                scrapedurl = "http://www.mitele.es" + match[0]
                #/directo/cuatro/
                patron  = '/directo/([^/]+)/'
                matches2 = re.findall(patron,match[0],re.DOTALL)
                if DEBUG: scrapertools.printMatches(matches2)
                scrapedtitle = ""
                if len(matches2)>0:
                    scrapedtitle = matches2[0]
                scrapedthumbnail = match[1]
                scrapedplot = ""
                itemlist.append( Item(channel=__channel__, action="playdirecto" , server="mitele", title=scrapedtitle,  fulltitle=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, show=scrapedtitle))
    else:
        return []
    return itemlist

def getXML(url):
    xml = ""
    try:
        data = scrapertools.cachePage(url)
    
        # Extrae las entradas (carpetas)       
        patron = 'var flashvars = {(.*?)}'
        matches = re.compile(patron,re.DOTALL).findall(data)
        logger.info("hay %d matches" % len(matches))        
    
        itemlist = []
        for match in matches:
            data2 = match
            patron  = '"host":"(.*?)".*?'
            matches2 = re.compile(patron,re.DOTALL).findall(data2)
    
            for match2 in matches2:
                xml = match2.replace("\\","")
                logger.info("XML = "+xml)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
    return xml 

def getciphertext(id, startTime, endTime):
    ciphertext = ""
    try:  
        request = urllib2.Request('http://servicios.telecinco.es/tokenizer/clock.php/')
        request.add_header('Accept-encoding', 'gzip')
        response = urllib2.urlopen(request)
       
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO( response.read())
            f = gzip.GzipFile(fileobj=buf)
            serverTime = f.read()
            
            data = serverTime+";"+id+";"+startTime+";"+endTime
            logger.info("Data = "+data)
    
            AES = aes.AES()  
            ciphertext = AES.encrypt(data,'xo85kT+QHz3fRMcHMXp9cA',256)       
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
    return ciphertext 

def getvideo(id,ciphertext,token):
    try:
        url = 'http://servicios.telecinco.es/tokenizer/tk' + str(token) + '.php'
        if token == 2:
            values = {'force_http' : '1',
          'sec' : ciphertext,
          'id' : id}
        else:
            values = {'force_http' : '1',
              'hash' : ciphertext,
              'id' : id}
        
        search_data = urllib.urlencode(values,doseq=True)
        request = urllib2.Request(url,search_data)
        request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)')
        response = urllib2.urlopen(request)
        data = response.read()
        response.close()   
        return data
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
    return ""      
        
def playvideo(item, data):
    itemlist = []
    
    try:
        patron = '<file>([^<]+)</file>'
        matches = re.compile(patron,re.DOTALL).findall(data)
        if len(matches)>0 :
            file = unescape(matches[0])
        else:
            patron = '<file[^>]+>([^<]+)</file>'
            matches = re.compile(patron,re.DOTALL).findall(data)
            file = unescape(matches[0])
        
        itemlist.append( Item(channel=__channel__, action="play" , server="mitele", title="play video", url=file, thumbnail=item.thumbnail, plot="", extra="", category=item.category, fanart=item.thumbnail, folder=False))
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
    return itemlist
            
def getrtmp(id, ciphertext, token):
    try:
        url = 'http://servicios.telecinco.es/tokenizer/tk' + str(token) + '.php'
        values = {'force_http' : '1',
          'directo' : ciphertext,
          'id' : id,
          'startTime' : '0',
          'endTime': '0'}
        search_data = urllib.urlencode(values,doseq=True)
        request = urllib2.Request(url,search_data)
        request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)')
        response = urllib2.urlopen(request)
        data = response.read()
        response.close()   
        return data
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
    return ""  
          
def playrtmptoken2(item, data):
    itemlist = []
    
    try:
        patron = '<stream>([^?]+)?([^<]+)</stream>'
        matches = re.compile(patron,re.DOTALL).findall(data)
        rtmp0 = matches[0][0]
        rtmp1 = matches[0][1]
        
        patron = '<file>([^<]+)</file>'
        matches = re.compile(patron,re.DOTALL).findall(data)
        if len(matches)>0 :
            file = unescape(matches[0])
        else:
            patron = '<file[^>]+>[^:]+:([^<]+)</file>'
            matches = re.compile(patron,re.DOTALL).findall(data)
            file = unescape(matches[0])
        
        rtmp = rtmp0 + "/" + file + rtmp1
    
        xbmcrtmp = rtmp0 + " playpath=" + file+rtmp1 + " swfUrl=\"http://static1.tele-cinco.net/comun/swf/playerMitele.swf\" pageUrl=\"" + item.url + "\" live=true"
        
        itemlist.append( Item(channel=__channel__, action="play" , server="mitele", title="play rtmp", url=xbmcrtmp, thumbnail=item.thumbnail, plot="", extra="", category=item.category, fanart=item.thumbnail, folder=False))
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)

    return itemlist

def playrtmptoken3(item, data):
    itemlist = []
    
    try:
        patron = '<stream>([^?]+)</stream>'
        matches = re.compile(patron,re.DOTALL).findall(data)
        stream = matches[0]
        
        patron = '<file>([^<]+)</file>'
        matches = re.compile(patron,re.DOTALL).findall(data)
        if len(matches)>0 :
            file = unescape(matches[0])
        else:
            patron = '<file[^>]+>[^:]+:([^<]+)</file>'
            matches = re.compile(patron,re.DOTALL).findall(data)
            file = unescape(matches[0])
        
        rtmp = stream + "/" + file
    
        xbmcrtmp = stream + " playpath=" + file + " swfUrl=\"http://static1.tele-cinco.net/comun/swf/playerMitele.swf\" pageUrl=\"" + item.url + "\" live=true"
        
        itemlist.append( Item(channel=__channel__, action="play" , server="mitele", title="play rtmp", url=xbmcrtmp, thumbnail=item.thumbnail, plot="", extra="", category=item.category, fanart=item.thumbnail, folder=False))
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)

    return itemlist

#unescapes all the xml formatted characters
def unescape(s):
    want_unicode = False
    if isinstance(s, unicode):
        s = s.encode("utf-8")
        want_unicode = True

    # the rest of this assumes that `s` is UTF-8
    list = []

    # create and initialize a parser object
    p = xml.parsers.expat.ParserCreate("utf-8")
    p.buffer_text = True
    p.returns_unicode = want_unicode
    p.CharacterDataHandler = list.append

    # parse the data wrapped in a dummy element
    # (needed so the "document" is well-formed)
    p.Parse("<e>", 0)
    p.Parse(s, 0)
    p.Parse("</e>", 1)

    # join the extracted strings and return
    es = ""
    if want_unicode:
        es = u""
    return es.join(list)

def test():

    # Al entrar sale una lista de programas
    mainlist_items = mainlist(Item())
    programas_items = series(mainlist_items[0])
    if len(programas_items)==0:
        print "La categoria '"+mainlist_item.title+"' no devuelve programas"
        return False

    temporadas_items = temporadas(programas_items[0])
    if len(temporadas_items)==0:
        print "El programa '"+programas_items[0].title+"' no devuelve temporadas"

    episodios_items = capitulos(temporadas_items[0])
    if len(episodios_items)==0:
        print "El programa '"+programas_items[0].title+"' temporada '"+temporadas_items[0].title+"' no devuelve episodios"

    return True