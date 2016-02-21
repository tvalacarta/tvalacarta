# -*- coding: utf-8 -*-

#------------------------------------------------------------

# pelisalacarta - XBMC Plugin

# creado por rsantaella

#------------------------------------------------------------



import urlparse,urllib2,urllib,re
import os, sys



from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools


__channel__ = "mundonick"
__category__ = "F"
__type__ = "generic"
__title__ = "mundonick"
__language__ = "ES"
__creationdate__ = "20121216"
__vfanart__ = ""
__urlbase__ = "http://www.mundonick.com"
__urlconfig__ = "http://intl.esperanto.mtvi.com/player/configuration.jhtml?"



DEBUG = config.get_setting("debug")

def isGeneric():

    return True

def mainlist(item):

    logger.info("[mundonick.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Destacados" , action="programas" , url="http://www.mundonick.com/nickturbo/?gid=2418", folder=True) )
    itemlist.append( Item(channel=__channel__, title="Estrenos"   , action="programas" , url="http://www.mundonick.com/nickturbo/?gid=2491", folder=True) )
    itemlist.append( Item(channel=__channel__, title="Toons"      , action="programas" , url="http://www.mundonick.com/nickturbo/?gid=2419", folder=True) )
    itemlist.append( Item(channel=__channel__, title="Series"     , action="programas" , url="http://www.mundonick.com/nickturbo/?gid=2420", folder=True) )
    itemlist.append( Item(channel=__channel__, title="Clásico"    , action="programas" , url="http://www.mundonick.com/nickturbo/?gid=2421", folder=True) )
    itemlist.append( Item(channel=__channel__, title="Nick Jr"    , action="programas" , url="http://www.mundonick.com/nickturbo/?gid=2821", folder=True) )

    return itemlist

def programas(item):

    logger.info("[mundonick.py] programas")
	
    data = scrapertools.cachePage(item.url)
	
    #logger.info(data)

    #<div class="thumbBigVideoTurbo"><a href="/nickturbo/?gid=2418&amp;cid=1697480"><img class="linkImgTurbo" src="/shared/media/images/shows/t/tortugas_ninja/107_1_232x150.jpg" alt="Las Tortugas Ninja | NUEVA SERIE !!!" title="Las Tortugas Ninja | NUEVA SERIE !!!">
    patron = '<div class="thumbBigVideoTurbo"><a href="([^"]+)"><img class="linkImgTurbo" src="([^"]+)" alt="(.*?)" title="(.*?)">'

    matches = re.compile(patron,re.DOTALL).findall(data)

    if DEBUG: scrapertools.printMatches(matches)
	
    itemlist = []
    for match in matches:
        scrapedurl = __urlbase__ + match[0].replace('&amp;','&');
        scrapedthumbnail = 	__urlbase__ + match[1]	
        scrapedtitle = scrapertools.htmlclean(match[3]).decode('iso-8859-1').encode("utf8","ignore")
        itemlist.append( Item(channel=__channel__, action="episodios", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail,  folder=True) )

    return itemlist

def episodios(item):

    logger.info("[mundonick.py] episodios")
	
    data = scrapertools.cachePage(item.url)
	
    #logger.info(data)

    #<a href=""><img class="linkImgTurbo" src="/shared/media/images/shows/l/legend_of_korra/101_3_82x55.jpg" alt="" title=""></a><a href="/nickturbo/?gid=2418&amp;cid=1696825&amp;vid=853875"><img class="linkImgTurbo" src="images/thumbsLitleFrame.png" alt="Legend Of Korra | Episodio 01" title="Legend Of Korra | Episodio 01"
    patron = '<a href=""><img class="linkImgTurbo" src="([^"]+)" alt="" title=""></a><a href="([^"]+)"><img class="linkImgTurbo" src="images/thumbsLitleFrame.png" alt="(.*?)" title="(.*?)"'

    matches = re.compile(patron,re.DOTALL).findall(data)

    if DEBUG: scrapertools.printMatches(matches)
	
    itemlist = []
    #video_urls = []
    for match in matches:
        scrapedurl = match[1].split('=')[3];
        scrapedthumbnail = 	__urlbase__ + match[0]	
        scrapedtitle = scrapertools.htmlclean(match[3]).decode('iso-8859-1').encode("utf8","ignore")
        itemlist.append( Item(channel=__channel__, action="play", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail,  folder=False) )
        #video_urls.append(get_video_url_internal(scrapedurl ))
    
    #for video_url in video_urls:
    #    logger.info(str(video_url))
    return itemlist

def get_episodio_complete_name(videoid):
    logger.info("[mundonick.py] get_episodio_complete_name")

    permalink = 'uri=mgid:uma:video:mundonick.com:' + videoid
	
    data = scrapertools.cachePage(__urlconfig__ + permalink)
    #logger.info(data)

    import xml.etree.ElementTree as xmlet
    configuration = xmlet.fromstring(data)
	
    #swfurl = configuration.find('.//player//URL').text
    feedurl = configuration.find('.//player//feed').text
	
    data = scrapertools.cachePage(feedurl)
    #logger.info(data)
    
    feed = xmlet.fromstring(data)
    description = feed.find('.//item/description').text.encode("utf8","ignore").replace('<i>', '').replace('</i>', ' |').replace('<br/>', ' ').replace('LA', '');
    #logger.info(description)
    return description 

def play(item):
    logger.info("[mundonick.py] play video: " + item.url)
    itemlist=[]

    permalink = 'uri=mgid:uma:video:mundonick.com:' + item.url
	
    data = scrapertools.cachePage(__urlconfig__ + permalink)
    if (data == ''):
        return itemlist
    #logger.info(data)

    import xml.etree.ElementTree as xmlet
    configuration = xmlet.fromstring(data)
	
    swfurl = configuration.find('.//player//URL').text
    feedurl = configuration.find('.//player//feed').text
	
    data = scrapertools.cachePage(feedurl)
    #logger.info(data)
    
    feed = xmlet.fromstring(data)
    description = feed.find('.//item/description').text.encode("utf8","ignore").replace('<i>', '').replace('</i>', ' |').replace('<br/>', ' ').replace('LA', '');
    #mediacontent = feed.find('{http://search.yahoo.com/mrss/}content').get('url')

    patron = '<media:content type="text/xml" isDefault="true"\nurl="([^"]+)">'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    if matches: mediacontent = matches[0]

    #data = scrapertools.cachePage(mediacontent)
    #logger.info(data)

    logger.info(description)
    itemlist.append( Item(channel=__channel__, action="play", title=description, url=mediacontent, server="mundonick", thumbnail=item.thumbnail,  folder=False) )
    return itemlist
	
def get_video_url_internal( page_url):
    logger.info("[mundonick.py] get_video_url(page_url='%s')" % page_url)
    
    video_file_info_url = 'http://intl.esperanto.mtvi.com/www/xml/media/mediaGen.jhtml?uri=mgid:uma:video:mundonick.com:%s' % page_url.split('=')[3]
    
    data = scrapertools.cachePage(video_file_info_url)

    #logger.info(data)
    
    #if data.find('video/x-flv')<0:
    #    finalurl=re.compile('<src>(.+?)</src>\n</rendition>\n<rendition cdn=".+?" duration=".+?" bitrate=".+?" width=".+?" height=".+?"\ntype="video/mp4">').findall(data)[-1]
    #    #logger.info("finalurl: " + finalurl)
    #else:
    #rendition cdn="akamai" duration="1380" width="448" height="336" type="video/x-flv" bitrate="650"
    swap=re.compile('<rendition cdn=".+?" duration=".+?" width=".+?" height=".+?" type="video/x-flv" bitrate=".+?">\n<src>(.+?)</src>\n</rendition>').findall(data)
    #if not swap: swap=re.compile('<src>(.+?)</src>').findall(data)
    #logger.info("swap: " + swap[0])

    return swap

def test():

    # Al entrar sale una lista de programas
    mainlist_items = mainlist(Item())
    for mainlist_item in mainlist_items:
        programas_items = programas(mainlist_item)

        if len(programas_items)==0:
            print "La categoria '"+mainlist_item.title+"' no devuelve programas"
            return False

    programas_items = programas(mainlist_items[-1])
    episodios_items = episodios(programas_items[0])
    if len(episodios_items)==0:
        print "El programa '"+programas_items[0].title+"' no devuelve episodios"

    return True