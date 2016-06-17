# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para CCTV
# creado por rsantaella
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "cctvspan"
__category__ = "F"
__type__ = "generic"
__title__ = "cctvspan"
__language__ = "ES"
__creationdate__ = "20121130"
__vfanart__ = "http://espanol.cntv.cn/library/column/2010/11/24/C28600/style/img/map2.jpg"

DEBUG = config.get_setting("debug")
MAIN_URL = "http://espanol.cctv.com/"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.cctvspan mainlist")
    return programas(Item())

def programas(item):
    logger.info("tvalacarta.cctvspan programas")

    itemlist = []
    if item.url=="":
        item.url = MAIN_URL

    '''
    <li><a href="http://cctvespanol.cntv.cn/" target="_blank">CCTV-Español</a>
    <div class="xiala">
    <dl id="up_box">
    <dd class=""><a href="http://cctv.cntv.cn/lm/cctvnoticias/index.shtml" target="_blank">CCTV Noticias</a></dd>
    ...
    </dl>
    </div>
    </li>
    '''
    # Descarga la pȧina
    data = scrapertools.cachePage(item.url)
    logger.info("data="+data)
    data = scrapertools.find_single_match(data,'<li><a href="http://cctvespanol.cntv.cn/[^>]+>CCTV-Espa[^<]+</a[^<]+<div class="xiala"[^<]+<dl id="up_box">(.*?)</dl>')
    logger.info("data="+data)
    patron = '<a href="([^"]+)"[^>]+>([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    item_series = None
    item_infantil = None

    for scrapedurl,scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        url   = urlparse.urljoin(item.url,scrapedurl)
        nuevo_item = Item(channel=__channel__, action="episodios", title=title , url=url , show=title, category="Programas", folder=True)

        if nuevo_item.title=="Hora Infantil":
            item_infantil = nuevo_item

        elif nuevo_item.title=="El Proyector":
            item_series = nuevo_item

        else:
            itemlist.append( nuevo_item )

    if item_series is not None:
        itemlist.extend(series(item_series))

    if item_infantil is not None:
        nuevo_item = Item(channel=__channel__, action="episodios", title="El mundo de la familia Tou-Paraíso de mascotas" , thumbnail="http://p1.img.cctvpic.com/photoAlbum/page/performance/img/2015/8/27/1440643997743_428.jpg", url=item_infantil.url , show="El mundo de la familia Tou-Paraíso de mascotas", category="infantil", folder=True)
        itemlist.append(nuevo_item)
        itemlist.extend(series(item_infantil,category="Infantil"))

    return itemlist

def detalle_programa(item):

    try:
        data = scrapertools.cache_page(item.url)
        #print data 

        item.thumbnail = scrapertools.find_single_match(data,'<div class="banner" style="background\:url\(([^\)]+)\)')

        url = scrapertools.find_single_match(data,'<a href="([^"]+)" target="_blank">Sobre el programa</a>')
        #print url 
        if url=="":
            item.plot = scrapertools.find_single_match(data,'<h3>Sobre el programa</h3>(.*?)</div>')
            item.plot = scrapertools.htmlclean(item.plot).strip()
        else:
            data = scrapertools.cache_page(url)
            item.plot = scrapertools.find_single_match(data,'<!--repaste.body.begin-->(.*?)<!--repaste.body.end-->')
            item.plot = scrapertools.htmlclean(item.plot).strip()
    except:
        pass

    return item

def series(item,category="Series"):
    logger.info("tvalacarta.cctvspan series")    

    '''
    <li>
    <div class="image">
    <a href="http://cctv.cntv.cn/lm/elproyector/especial/EmigracinalOcanodeSur/index.shtml" target="_blank"><img width="184" height="253" src="http://p5.img.cctvpic.com/photoAlbum/page/performance/img/2014/9/15/1410746648085_93.jpg"></a>
    <a class="plus" href="http://cctv.cntv.cn/lm/elproyector/especial/EmigracinalOcanodeSur/index.shtml" target="_blank"></a>
    </div>
    <div class="text">
    <h3><a href="http://cctv.cntv.cn/lm/elproyector/especial/EmigracinalOcanodeSur/index.shtml" target="_blank">Emigración al Océano de Sur</a></h3>
    <p><a href="http://cctv.cntv.cn/lm/elproyector/especial/EmigracinalOcanodeSur/index.shtml" target="_blank"></a></p>
    <p><a href="http://cctv.cntv.cn/lm/elproyector/especial/EmigracinalOcanodeSur/index.shtml" target="_blank">Nº de capítulos: 38</a></p>
    </div>
    </li>
    '''
    # Descarga la pagina
    data = scrapertools.cachePage(item.url)
    patron  = '<li[^<]+'
    patron += '<div class="image"[^<]+'
    patron += '<a href="([^"]+)[^>]+><img width="[^"]+" height="[^"]+" src="([^"]+)"></a[^<]+'
    patron += '<a[^<]+</a[^<]+'
    patron += '</div[^<]+'
    patron += '<div class="text"[^<]+'
    patron += '<h3><a[^>]+>([^<]+)</a>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    
    itemlist = []
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:

        title = scrapertools.htmlclean(scrapedtitle)
        url = scrapedurl
        thumbnail = scrapedthumbnail

        if url.startswith("http://cctv"):
            itemlist.append( Item(channel=__channel__, action="episodios", title=title , url=url , thumbnail=thumbnail, show=title, category=category, folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.cctvspan episodios")    
    itemlist = []

    '''
    <div class="text_lt">
    <a guid="40f061633e614ffe829ab3df91279b44" style="cursor:pointer;" onclick="loadvideo('40f061633e614ffe829ab3df91279b44')"><img src="http://p2.img.cctvpic.com/photoworkspace/2015/03/15/2015031515100374890.bmp" width="96" height="75" class="l" /></a>
    <h3><a onclick="loadvideo('40f061633e614ffe829ab3df91279b44')" style="cursor:pointer;">EXTRANJEROS EN CHINA 03/15/2015 Liz Vargas, Profesora de la Universidad de Estudios Internacionales de Beijing</a></h3>
    '''
    # Descarga la pȧina
    data = scrapertools.cachePage(item.url)
    patron  = '<div class="text_lt"[^<]+'
    patron += '<a guid="([^"]+)"[^<]+<img src="([^"]+)"[^<]+</a[^<]+'
    patron += '<h3><a[^>]+>([^<]+)</a>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    
    for guid,scrapedthumbnail,scrapedtitle in matches:

        title = scrapertools.htmlclean(scrapedtitle)
        url = guid
        thumbnail = scrapedthumbnail
        aired_date = scrapertools.parse_date(scrapedtitle,"mdy")
        itemlist.append( Item(channel=__channel__, action="play", server="cntv", title=title , url=url , thumbnail=thumbnail, show=item.show, aired_date=aired_date, folder=False) )

    '''
    <span class="text_lt">
    <h3><a href="http://cctv.cntv.cn/2015/03/31/VIDE1427774161717552.shtml" target="_blank">ECONOMÍA  AL DÍA 03/31/2015 11：00</a></h3>
    '''
    patron  = '<span class="text_lt"[^<]+'
    patron += '<h3><a href="([^"]+)"[^>]+>([^<]+)</a>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    
    for scrapedurl,scrapedtitle in matches:

        title = scrapertools.htmlclean(scrapedtitle)
        url = scrapedurl
        thumbnail = ""
        aired_date = scrapertools.parse_date(scrapedtitle,"mdy")
        itemlist.append( Item(channel=__channel__, action="play", server="cntv", title=title , url=url , thumbnail=thumbnail, show=item.show, aired_date=aired_date, folder=False) )


    '''
    <li>
    <a href="http://cctv.cntv.cn/2015/08/21/VIDE1440121441066290.shtml" target="_blank">
    <img src="http://p1.img.cctvpic.com/photoworkspace/2015/08/21/2015082114203738064.jpg" width="151" height="110" />
    </a>
    <div class="tp1"><a href="http://cctv.cntv.cn/2015/08/21/VIDE1440121441066290.shtml" target="_blank">
    </a>
    </div>
    <div class="tp2">
    <a href="http://cctv.cntv.cn/2015/08/21/VIDE1440121441066290.shtml" target="_blank">
    NIHAO CHINA 08/21/2015 Viajando y Aprendiendo Chino-Palabras y frases sobre mobiliarios
    </a></div></li>
    '''
    patron  = '<li[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '</a[^<]+'
    patron += '<div class="tp1"><a[^<]+'
    patron += '</a[^<]+'
    patron += '</div[^<]+'
    patron += '<div class="tp2"[^<]+'
    patron += '<a[^>]+>([^<]+)</a>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:

        title = scrapertools.htmlclean(scrapedtitle)
        url = scrapedurl
        thumbnail = scrapedthumbnail
        aired_date = scrapertools.parse_date(scrapedtitle,"mdy")
        itemlist.append( Item(channel=__channel__, action="play", server="cntv", title=title , url=url , thumbnail=thumbnail, show=item.show, aired_date=aired_date, folder=False) )

    # Prueba a ver si es la página de una serie
    if len(itemlist)==0:
        itemlist = episodios_serie(item,data)

    return itemlist

def detalle_episodio(item):

    item.geolocked = "0"

    if item.aired_date == "":
        item.aired_date = scrapertools.parse_date(item.title,"mdy")

    try:
        from servers import cntv as servermodule
        video_urls = servermodule.get_video_url(item.url)
        item.media_url = video_urls[0][1]
    except:
        import traceback
        print traceback.format_exc()
        item.media_url = ""

    return item

def episodios_serie(item,data):
    logger.info("tvalacarta.cctvspan episodios_serie")    

    '''
    <div class="list_box" style="display:block">
    <div class="lanmugwZ10483_con01" style="background:block;width:357;height:381;">
    <div class="box03">
    <div class="text"><A guid="07c3ff69b66f412287de977c6ac58fb5" onclick="loadvideo('07c3ff69b66f412287de977c6ac58fb5');" href="javascript:void(0);" name="">1</A><A guid="05bcab043fed4032a2194051a4dd1c47" onclick="loadvideo('05bcab043fed4032a2194051a4dd1c47');" href="javascript:void(0);" name="">2</A><A guid="4fa2cb1ff40043fcaa505eb24c0fd63d" onclick="loadvideo('4fa2cb1ff40043fcaa505eb24c0fd63d');" href="javascript:void(0);" name="">3</A><A guid="909a80cbe038443aa20511330ebaeb3d" onclick="loadvideo('909a80cbe038443aa20511330ebaeb3d');" href="javascript:void(0);" name="">4</A><A guid="620505788b7846bba209306c5f92123d" onclick="loadvideo('620505788b7846bba209306c5f92123d');" href="javascript:void(0);" name="">5</A><A guid="6d5c99daaa9548d7a4e89160a564c624" onclick="loadvideo('6d5c99daaa9548d7a4e89160a564c624');" href="javascript:void(0);" name="">6</A><A guid="a167205d4d7d44bb8a2be82f3d89c48f" onclick="loadvideo('a167205d4d7d44bb8a2be82f3d89c48f');" href="javascript:void(0);" name="">7</A><A guid="87d7b9b30f614ad885a2fe4ac4682ee8" onclick="loadvideo('87d7b9b30f614ad885a2fe4ac4682ee8');" href="javascript:void(0);" name="">8</A><A guid="49f9223f83434a87a3fa7b11c5ea7e7d" onclick="loadvideo('49f9223f83434a87a3fa7b11c5ea7e7d');" href="javascript:void(0);" name="">9</A><A guid="cb6ce3197da84d20b42c7592270fd1f1" onclick="loadvideo('cb6ce3197da84d20b42c7592270fd1f1');" href="javascript:void(0);" name="">10</A><A guid="08d2add80fce406291fb59fef0af49d5" onclick="loadvideo('08d2add80fce406291fb59fef0af49d5');" href="javascript:void(0);" name="">11</A><A guid="000ae1094a464c44b2c16ad9b6db9a09" onclick="loadvideo('000ae1094a464c44b2c16ad9b6db9a09');" href="javascript:void(0);" name="">12</A><A guid="398ef05cb8194044aa5acce3bda5bb01" onclick="loadvideo('398ef05cb8194044aa5acce3bda5bb01');" href="javascript:void(0);" name="">13</A><A guid="18a574abafcb492d8b1c440c0e03f0fe" onclick="loadvideo('18a574abafcb492d8b1c440c0e03f0fe');" href="javascript:void(0);" name="">14</A><A guid="ed4948e6783348598ff321f4490a277b" onclick="loadvideo('ed4948e6783348598ff321f4490a277b');" href="javascript:void(0);" name="">15</A><A guid="4dbe4c076ac8460496727bf7705248de" onclick="loadvideo('4dbe4c076ac8460496727bf7705248de');" href="javascript:void(0);" name="">16</A><A guid="05d3b39d808f4e2596606d4692b063ed" onclick="loadvideo('05d3b39d808f4e2596606d4692b063ed');" href="javascript:void(0);" name="">17</A><A guid="9253d2398e70406dbbbe3bed4085a2db" onclick="loadvideo('9253d2398e70406dbbbe3bed4085a2db');" href="javascript:void(0);" name="">18</A><A guid="bfbde6475dbf461cb2ae2e51544cdf0c" onclick="loadvideo('bfbde6475dbf461cb2ae2e51544cdf0c');" href="javascript:void(0);" name="">19</A><A guid="db7d3d3e526d46c9bae09911edab8529" onclick="loadvideo('db7d3d3e526d46c9bae09911edab8529');" href="javascript:void(0);" name="">20</A><A guid="849c52f0b3a949b8885a86336c8d550c" onclick="loadvideo('849c52f0b3a949b8885a86336c8d550c');" href="javascript:void(0);" name="">21</A><A guid="47b79bdea3fd4294b081366fb2462ecf" onclick="loadvideo('47b79bdea3fd4294b081366fb2462ecf');" href="javascript:void(0);" name="">22</A><A guid="3e97008f8c6f4f16a5d1b3d28ad24b02" onclick="loadvideo('3e97008f8c6f4f16a5d1b3d28ad24b02');" href="javascript:void(0);" name="">23</A><A guid="437bcf9eca72462b8d3e6034e2df2691" onclick="loadvideo('437bcf9eca72462b8d3e6034e2df2691');" href="javascript:void(0);" name="">24</A><A guid="d6122e3e570a45a48eb3aba3918d74a6" onclick="loadvideo('d6122e3e570a45a48eb3aba3918d74a6');" href="javascript:void(0);" name="">25</A></div>
    </div>
    </div>
    </div>

    </div>
    '''
    # Descarga la pȧina
    #data = scrapertools.cachePage(item.url)
    bloque = scrapertools.find_single_match(data,'<div class="box03">(.*?)</div>')
    patron  = '<A guid="([^"]+)"[^>]+>([^<]+)</A>'

    matches = re.compile(patron,re.DOTALL).findall(bloque)
    if DEBUG: scrapertools.printMatches(matches)
    
    itemlist = []
    for scrapedurl,scrapedtitle in matches:

        title = scrapertools.htmlclean(scrapedtitle)
        url = scrapedurl
        thumbnail = ""
        itemlist.append( Item(channel=__channel__, action="play", server="cntv", title=title , url=url , thumbnail=thumbnail, show=item.show, folder=False) )

    if len(itemlist)>0:
        return itemlist

    '''
    <li>
    <div class="image"><a href="http://espanol.cntv.cn/program/Telenovela/20130121/105582.shtml" target="_blank" title=""><img src="http://p3.img.cctvpic.com/fmspic/2013/01/21/c496264b7c4546e2a99f6bc33c7a8c86-180.jpg" width="106"  alt="La contrasena de la felicidad Capítulo 27" /></a></div>
    <div class="text">
    <a href="http://espanol.cntv.cn/program/Telenovela/20130121/105582.shtml" target="_blank" title="">La contrasena de la felicidad Capítulo 27</a>
    </div>
    </li>
    '''
    bloque = scrapertools.find_single_match(data,'<div class="image_list_box"(.*?)</ul[^<]+</div')
    logger.info("bloque="+bloque)
    patron  = '<a href="([^"]+)"[^<]+<img src="([^"]+)" width="[^"]+"\s+alt="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(bloque)
    if DEBUG: scrapertools.printMatches(matches)
    
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        url = scrapedurl
        thumbnail = scrapedthumbnail
        itemlist.append( Item(channel=__channel__, action="play", server="cntv", title=title , url=url , thumbnail=thumbnail, show=item.show, folder=False) )

    return itemlist

def play(item):

    item.server="cntv";
    itemlist = [item]

    return itemlist

# Test de canal
# Devuelve: Funciona (True/False) y Motivo en caso de que no funcione (String)
def test():
    
    items_programas = programas(Item())

    # El canal tiene estructura programas -> episodios -> play
    if len(items_programas)==0:
        return False,"No hay programas"

    items_episodios = episodios(items_programas[0])
    if len(items_episodios)==0:
        return False,"No hay episodios en "+items_programas[0].title

    item_episodio = detalle_episodio(items_episodios[0])
    if item_episodio.media_url=="":
        return False,"El conector no devuelve enlace para el vídeo "+item_episodio.title

    return True,""
