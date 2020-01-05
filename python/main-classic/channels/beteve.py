# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para beteve
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "beteve"

def mainlist(item):
    logger.info("tvalacarta.channels.beteve mainlist")

    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.beteve programas")

    item = Item(url="https://beteve.cat/programes/")

    itemlist = []

    encontrados = dict()

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    # Parse
    '''
    <div class="col-12 col-sm-6 col-md-4 col-lg-3">
    <a href="/habitacio-910/"/>
    <div class="btv-programa-name-container text-center" style="background-image: url(https://img.beteve.cat/wp-content/uploads/2018/06/header-web-habitacio-910-1920x1080.jpg);"><span>Habitació 910</span>
    '''
    patron  = '<div class="col-12[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<div class="btv-programa-name-container text-center" style="background-image. url\(([^\)]+)\)[^<]+'
    patron += '<span>([^<]+)</span[^<]+'

    matches = scrapertools.find_multiple_matches(data,patron)

    for scraped_url,thumbnail,title in matches:
        url = urlparse.urljoin(item.url,scraped_url)

        encontrados[url] = True

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail=thumbnail, action="episodios", show=title, folder=True) )

    '''
    <div class="col-12 col-sm-6 col-md-4 my-3 mb-sm-0">
    <img class="btv-programes-item-img " src="https://beteve.cat/wp-content/themes/beteve/img/icona-programacio-video-on.svg">
    <img class="btv-programes-item-img btv-programes-item-img-off" src="https://beteve.cat/wp-content/themes/beteve/img/icona-programacio-audio-off.svg">
    <a href="/nit-a-la-terra/" class="btv-programes-item">                                            
    <span>Nit a la Terra</span>
    </a>
    '''

    patron  = '<div class="col-12[^<]+'
    patron  = '<img class="btv-programes-item-img[^<]+'
    patron  = '<img class="btv-programes-item-img[^<]+'
    patron += '<a href="([^"]+)" class="btv-programes-item"[^<]+'
    patron += '<span>([^<]+)</span[^<]+'

    matches = scrapertools.find_multiple_matches(data,patron)

    for scraped_url,title in matches:
        url = urlparse.urljoin(item.url,scraped_url)

        if url in encontrados:
            continue

        encontrados[url] = True

        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url, thumbnail="", action="episodios", show=title, folder=True) )
    
    itemlist = sorted(itemlist, key=lambda Item: Item.title)

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.beteve episodios")

    itemlist = []
    
    # Descarga la página

    #https://beteve.cat/la-porteria/
    #https://beteve.cat/wp-content/ajax-email.php?action=btv_search_posts_by_input_text&btv_search_text=&btv_taxonomy=programa&btv_slug=la-porteria&btv_page_num=0&btv_date_start=&btv_date_end=

    if not "ajax-email.php" in item.url:
        partes = item.url.split("/")
        slug = partes[-1]
        if slug=="":
            slug = partes[-2]

        page_url = "https://beteve.cat/wp-content/ajax-email.php?action=btv_search_posts_by_input_text&btv_search_text=&btv_taxonomy=programa&btv_slug="+slug+"&btv_page_num=0&btv_date_start=&btv_date_end="
    else:
        page_url = item.url

    data = scrapertools.cache_page(page_url)

    # Parse
    '''
    <div class="d-lg-none d-xl-none col-12 btv-portada-programa-posts-content-container-mobile mb-3">
    <div class="row bg-white p-2">
    <div class="col-4 pr-0">
    <a href="https://beteve.cat/la-porteria/la-porteria-472/"><div class="btv-portada-programa-posts-content-img-mobile" style="background-image: url('https://cdnsecakmi.kaltura.com/p/2346171/thumbnail/entry_id/1_6y9pn2ls/width/300/3siSO.jpg');"></div></a>
    </div>
    <div class="col-8 pl-0">
    <div class="btv-portada-programa-posts-info-container-mobile">
    <span class="btv-portada-programa-posts-info-category-mobile"> </span>
    <span class="btv-portada-programa-posts-info-date-mobile d-inline-block"> 14 de desembre de 2018</span>
    <a href="https://beteve.cat/la-porteria/la-porteria-472/"><p>La porteria</p></a>
    </div>
    </div>
    </div>
    </div>
    '''
    patron  = '<a href="([^"]+)"[^<]+'
    patron += '<div class="btv-portada-programa-posts-content-img-mobile" style="background-image. '
    patron += "url.'([^']+)'.[^<]+</div></a[^<]+"
    patron += '</div[^<]+'
    patron += '<div class="col-8 pl-0"[^<]+'
    patron += '<div class="btv-portada-programa-posts-info-container-mobile"[^<]+'
    patron += '<span class="btv-portada-programa-posts-info-category-mobile"[^<]+</span[^<]+'
    patron += '<span class="btv-portada-programa-posts-info-date-mobile d-inline-block">([^<]+)</span[^<]+'
    patron += '<a[^<]+<p>([^<]+)</p></a[^<]+'

    matches = scrapertools.find_multiple_matches(data,patron)

    for scraped_url,thumbnail,scraped_date,scraped_title in matches:
        url = urlparse.urljoin(item.url,scraped_url)
        title = scraped_title.strip()+" "+scraped_date.strip()
        aired_date = scrapertools.parse_date(scraped_date)
        itemlist.append( Item(channel=CHANNELNAME, action="play", server="beteve", title=title, show=item.show, url=url, thumbnail=thumbnail, aired_date=aired_date, folder=False))

    current_page = scrapertools.find_single_match(page_url,'btv_page_num.(\d+)')
    if len(itemlist)>0 and current_page!="":
        next_page = str(int(current_page)+1)
        next_page_url = page_url.replace("btv_page_num="+current_page,"btv_page_num="+next_page)
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , url=next_page_url, action="episodios", show=item.show, folder=True) )

    return itemlist
