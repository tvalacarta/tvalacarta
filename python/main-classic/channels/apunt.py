# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para apunt
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "apunt"
LIVE_URL = "https://cflive-emea.live-delivery.ooyala.com/out/u/jb44pwd2tj7w5/111819/wyYXIxZTE6okZbyKLzxq8TXa4a-SQlAO/cs/d77d4356674b449695b1c0f19fbd6fae.m3u8"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.apunt mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Ver señal en directo" , action="play", url=LIVE_URL, category="programas", folder=False) )
    itemlist.append( Item(channel=CHANNELNAME, title="A la carta" , action="programas_apunt", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="La Colla" , action="programas_lacolla", folder=True) )

    return itemlist

def programas_apunt(item):
    logger.info("tvalacarta.channels.apunt programas_apunt")

    item.url = "https://apuntmedia.es/va/a-la-carta/programes/vist-en-tv"
    itemlist = parse_programas(item)

    itemlist.append( Item(channel=CHANNELNAME, title="Documentals" , url="https://apuntmedia.es/va/a-la-carta/documentals", action="episodios", show="Documentals", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Retransmissions" , url="https://apuntmedia.es/va/a-la-carta/retransmissions", action="episodios", show="Retransmissions", folder=True) )

    return itemlist

def programas_lacolla(item):
    logger.info("tvalacarta.channels.apunt programas_lacolla")

    item.url = "https://apuntmedia.es/va/la-colla/preescolar"
    itemlist = parse_programas(item)

    item.url = "https://apuntmedia.es/va/la-colla/infantil"
    itemlist.extend(parse_programas(item,itemlist))

    item.url = "https://apuntmedia.es/va/la-colla/angles"
    itemlist.extend(parse_programas(item,itemlist))

    return itemlist


def parse_programas(item,previous_items=[]):
    logger.info("tvalacarta.channels.apunt programas url="+item.url)

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    # Parse
    '''
    <div class="module videoprogram" id="video-137">
    <a href="/va/a-la-carta/programes/vist-en-tv/assumptes-interns" class="photo">
    <img title="Assumptes interns" alt="" src="https://apuntmedia.es/images/IMG000013214.png" />
    </a>
    <h2><a href="/va/a-la-carta/programes/vist-en-tv/assumptes-interns" class="programTitle itemTit" videoid="video-137">Assumptes interns</a></h2>
    <a href="/va/a-la-carta/programes/vist-en-tv/assumptes-interns"><p title="Pere Aznar fa un repàs diari de l’actualitat valenciana i de tot el món, amb una mirada divertida, sarcàstica i descarada. <strong>Dilluns a divendres a les 20:20h.</strong>">Pere Aznar fa un repàs diari de l’actualitat valenciana i de tot el món, amb una mirada divertida, sarcàstica i descarada. <strong>Dilluns a divendres a les 20:20h.</strong></p></a>
    </div>
    '''

    '''
    <div class="module videoprogram" id="video-77">
    <a href="/va/la-colla/preescolar/trip-i-troop" class="photo">
    <img title="Trip i Troop" alt="" src="https://apuntmedia.es/images/IMG000002367.jpg" />
    </a>
    <h2><a href="/va/la-colla/preescolar/trip-i-troop" class="programTitle itemTit" videoid="video-77">Trip i Troop</a></h2>
    <a href="/va/la-colla/preescolar/trip-i-troop"><p title="Si vols aprendre a conéixer els animals i les seues característiques d'una manera senzilla i entretinguda, Trip i Troop és la teua sèrie!">Si vols aprendre a conéixer els animals i les seues característiques d'una manera senzilla i entretinguda, Trip i Troop és la teua sèrie!</p></a>
    </div>
    '''
    patron  = '<div class="module videoprogram" id="video[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img title="[^"]+" alt="" src="([^"]+)"[^<]+'
    patron += '</a[^<]+'
    patron += '<h2><a[^>]+>([^<]+)</a></h2[^<]+'
    patron += '<a[^>]+><p title=".*?">(.*?)</p></a>'
    matches = scrapertools.find_multiple_matches(data,patron)

    for scraped_url,thumbnail,title,scraped_plot in matches:
        url = urlparse.urljoin(item.url,scraped_url)
        plot = scrapertools.htmlclean(scraped_plot)

        for previous_item in previous_items:
            if previous_item.title == title:
                logger.info("Duplicado "+title)
                continue

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, plot=plot, action="episodios", show=title, folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.apunt episodios")

    itemlist = []
    
    # Descarga la página
    data = scrapertools.cache_page(item.url)

    # Parse
    '''
    <div class="module" id="video-19425">
    <a href="/va/a-la-carta/programes/vist-en-tv/el-mati-a-punt/05-12-2018-el-mati-a-punt" class="photo">
    <div class="imgcontainer">
    <img src="https://secure-cf-c.ooyala.com/VrMHByZzE6jOLo7c-cmV5HkBMt1stm_T/3Gduepif0T1UGY8H4xMDoxOjA4MTsiGN" alt="" />
    </div>
    <span class='time'>03:01:30</span>
    </a><span class="category" style="background-color:#008CD6; color:#FFFFFF " >A la carta</span><a href="/va/a-la-carta/programes/vist-en-tv/el-mati-a-punt" title="El matí À Punt" class="inherit"><span>El matí À Punt</span></a><p><a class="itemTit" href="/va/a-la-carta/programes/vist-en-tv/el-mati-a-punt/05-12-2018-el-mati-a-punt" videoid="video-19425">05.12.2018 | El Matí À Punt</a></p> 
    <p title="Programa complet d'El Matí À Punt del dimecres 5 de desembre de 2018.">Programa complet d'El Matí À Punt del dimecres 5 de desembre de 2018.</p>
    <ul><li><a href="#"><span class="icon fa-heart-o" videoid="19425"></span></a></li> <li><a href="#">
    <span  newtitle="05.12.2018 | El Matí À Punt" destiny ="https://www.apuntmedia.es/va/a-la-carta/programes/vist-en-tv/el-mati-a-punt/05-12-2018-el-mati-a-punt" class="icon fa-share-alt"></span></a></li></ul>
    </div>
    '''
    patron  = '<div class="module" id="video-[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<div class="imgcontainer"[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '</div[^<]+'
    patron += "<span class='time'>([^<]+)</span.*?"
    patron += '<p title=[^>]+>(.*?)</p>.*?'
    patron += 'newtitle="(.*?)" destiny'

    matches = scrapertools.find_multiple_matches(data,patron)

    for scraped_url,thumbnail,duration,scraped_plot,title in matches:
        url = urlparse.urljoin(item.url,scraped_url)
        plot = scrapertools.htmlclean(scraped_plot)
        aired_date = scrapertools.parse_date(title)
        itemlist.append( Item(channel=CHANNELNAME, action="play", server="apunt", title=title, plot=plot, show=item.show, url=url, thumbnail=thumbnail, duration=duration, aired_date=aired_date, folder=False))

    next_page_url = scrapertools.find_single_match(data,'<a class="flechapaginado" href="([^"]+)"')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        if next_page_url!=item.url and not next_page_url.endswith("/0"):
            itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , url=next_page_url, action="episodios", show=item.show, folder=True) )

    return itemlist

def directos(item=None):
    logger.info("tvalacarta.channels.aragontv directos")

    itemlist = []

    itemlist.append( Item(channel=CHANNELNAME, title="À punt",   url=LIVE_URL, thumbnail="http://media.tvalacarta.info/canales/128x128/apunt.png", category="Autonómicos", action="play", folder=False ) )

    return itemlist
