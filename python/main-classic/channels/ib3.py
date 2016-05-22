# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para IB3
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = True
CHANNELNAME = "ib3"
MAIN_URL = "http://ib3tv.com/carta"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.ib3 mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Programes de producció pròpia"                    , action="categoria" , extra="Programes", url=MAIN_URL, folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Sèries de producció pròpia"                       , action="categoria" , extra="Sèries", url=MAIN_URL, folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Notícies / Programes d'actualitat"                , action="categoria" , extra="Informatius", url=MAIN_URL, folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Programes d'Esports / Retransmissions esportives" , action="categoria" , extra="Esports", url=MAIN_URL, folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Retransmissions"                                  , action="categoria" , extra="Retransm.", url=MAIN_URL, folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Documentals / Especials"                          , action="categoria" , extra="Documentals", url=MAIN_URL, folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Programes [A-Z] (thumbnail)"                      , action="programas" , url=MAIN_URL, folder=True) )

    return itemlist

def categoria(item):
    logger.info("tvalacarta.channels.ib3 categoria")
    itemlist=[]

    # Descarga la página
    item.url = MAIN_URL
    data = scrapertools.cache_page(item.url)
    data = scrapertools.get_match(data,'<li><a href="">'+item.extra+'</a>(.*?)</div>')
    #logger.info(data)

    # Extrae los programas
    '''
    <li><a href="">Pr</a>
    <div>
    <p>Programes de producció pròpia</p>
    <ul>
    <li><a href="javascript:stepcarousel.loadcontent('f-slide', '/wp-content/themes/ib3tv/carta/update.php?programId=7326efc5-93ce-4904-9571-a53d19c70217')">AIXÒ ÉS MEL</a></li>
    <li><a href="javascript:stepcarousel.loadcontent('f-slide', '/wp-content/themes/ib3tv/carta/update.php?programId=01e0e6c9-b2fd-4f5e-8641-17e3e455a553')">AIXÒ ÉS TOT</a></li>
    <li><a href="javascript:stepcarousel.loadcontent('f-slide', '/wp-content/themes/ib3tv/carta/update.php?programId=ff2ec1f6-a5ee-4d4d-b864-013f125c088a')">AIXÒ NO ÉS ISLÀNDIA</a></li>
    '''
    patron = "<li><a href=\"javascript.stepcarousel.loadcontent\('f-slide', '([^']+)'\)\">(.*?)</li>"
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle).strip()
        
        #/wp-content/themes/ib3/carta/update.php?programId=2d15fe76-bbed-40c9-95e3-32a800174b7c
        #http://ib3tv.com/wp-content/themes/ib3/carta/update.php?programId=e8f6d4ec-1d7c-4101-839a-36393d0df2a8
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = ""
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="episodios" , url=url, page=url , thumbnail=thumbnail, plot=plot , show=title , category = "programas" , folder=True) )

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.ib3 programlist")
    itemlist=[]

    # Descarga la página
    item.url = MAIN_URL
    data = scrapertools.cache_page(item.url)
    data = scrapertools.get_match(data,'<h1>Recerca programes(.*?)<div class="end"')
    #logger.info(data)

    # Extrae los programas
    patron  = '<div class="mielement"[^<]+'
    patron += '<div class="shadow"[^<]+'
    patron += "<a href=\"javascript.stepcarousel.loadcontent\('f-slide', '([^']+)'\)\">"
    patron += '<img src="([^"]+)"[^<]+</a[^<]+'
    patron += '</div[^<]+'
    patron += '<div class="nombres"><strong>([^<]+)</strong>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapedtitle.strip()
        #/wp-content/themes/ib3/carta/update.php?programId=2d15fe76-bbed-40c9-95e3-32a800174b7c
        #http://ib3tv.com/wp-content/themes/ib3/carta/update.php?programId=e8f6d4ec-1d7c-4101-839a-36393d0df2a8
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail
        plot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="episodios" , url=url, page=url , thumbnail=thumbnail, plot=plot , show=title , category = "programas" , folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.ib3 episodios")

    itemlist = []

    # Descarga la página
    headers = []
    headers.append(["Accept","*/*"])
    headers.append(["Accept-Encoding","gzip,deflate"])
    headers.append(["Accept-Language","es-ES,es;q=0.8,en;q=0.6"])
    headers.append(["Connection","keep-alive"])
    headers.append(["Referer","http://ib3tv.com/carta"])
    headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36"])
    headers.append(["X-Requested-With","XMLHttpRequest"])

    data = scrapertools.cachePage(item.url,headers=headers)
    logger.info(data)

    # Extrae los capítulos
    '''
    <div class="keyelement">
    <div class="keyimage">
    <div class="shadow">
    <a href="javascript:CambiaGraf('7e10a2b1-29a6-4c59-9bc0-77be28888cf6')" ><img src="http://media.ib3alacarta.com/e8f6d4ec-1d7c-4101-839a-36393d0df2a8/7e10a2b1-29a6-4c59-9bc0-77be28888cf6/5120551.jpg" width="190" height="120"/></a>
    </div>
    </div>	
    <div  class="keytext">
    <font color="#c6006f"><strong><b>Au idò!</b></strong></font>
    <br />
    <font color="#000000"></font>
    <br />
    <font size="0.5">02 06 2011 - Capítol: 57</font>
    </div>
    </div>
    '''
    '''
    <div class="keyelement">
    <div class="keyimage">
    <div class="shadow">    

    <a href="javascript:CambiaGraf('0f8a716f-d03b-4e02-84e9-48cba55cd576','Això és Tot! | Cap: 67')" ><img src="http://media.ib3alacarta.com/01e0e6c9-b2fd-4f5e-8641-17e3e455a553/0f8a716f-d03b-4e02-84e9-48cba55cd576/4266329.jpg" height="120px" " width="190"/></a>
    </div>
    </div>  
    <div  class="keytext">
    <font color="#c6006f" size="2.5"><strong>Això és Tot!</strong></font>
    <br />
    <font color="#595959">Això és Tot!</font>
    <br />
    <font size="0.5">03 11 2010 - Capítol: 67</font>
    </div>
    </div>
    '''
    patron  = '<div class="keyelement"[^<]+'
    patron += '<div class="keyimage"[^<]+'
    patron += '<div class="shadow"[^<]+'
    patron += '<a href="javascript:CambiaGraf.\'([^\']+)\',\'[^\']+\'." ><img src="([^"]+)"[^<]+</a>[^<]+'
    patron += '</div>[^<]+'
    patron += '</div>[^<]+'
    patron += '<div  class="keytext">(.*?)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    
    # Extrae los items
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle).strip()
        title = re.compile("\s+",re.DOTALL).sub(" ",title)
        url = "http://ib3tv.com/wp-content/themes/ENS/carta/titulos.php?type=TV&id="+scrapedurl
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append( Item(channel=CHANNELNAME, title=title , fulltitle = item.show + " - " + title , action="play" , page = url, url=url, thumbnail=thumbnail, show=item.show , plot=plot , folder=False) )

    return itemlist

def play(item):
    logger.info("tvalacarta.channels.ib3 play")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info("data="+data)
    #'src', "http://media.ib3alacarta.com/ff2ec1f6-a5ee-4d4d-b864-013f125c088a/7d3a82fb-6c03-4500-8c65-5ea510c61420/5018376.mp4"
    mediaurl = scrapertools.get_match(data,"file:'([^']+)',")
    itemlist.append( Item(channel=CHANNELNAME, title=item.title , action="play" , server="directo" , url=mediaurl, thumbnail=item.thumbnail, show=item.show , folder=False) )
    
    return itemlist

def test():

    # Comprueba que la primera opción tenga algo
    mainlist_items = mainlist(Item())
    for mainlist_item in mainlist_items:
        exec "programas_items = "+mainlist_item.action+"(mainlist_item)"
        if len(programas_items)==0:
            print "La opción "+mainlist_item.title+" no tiene programas"
            return False

    exec "programas_items = "+mainlist_items[0].action+"(mainlist_items[0])"
    episodios_items = episodios(programas_items[0])
    if len(episodios_items)==0:
        print "El programa "+programas_items[0].title+" no tiene episodios"
        return False

    videos_items = play(episodios_items[0])
    if len(episodios_items)==0:
        print "El episodio "+episodios_items[0].title+" del programa "+programas_items[0].title+" no tiene videos"
        return False

    return True