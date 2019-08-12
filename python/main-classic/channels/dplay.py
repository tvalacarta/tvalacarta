# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para dplay
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import re, urllib, urlparse

from core import logger
from core import scrapertools
from core import config
from core.item import Item
from servers import servertools

logger.info("tvalacarta.channels.dplay init")

DEBUG = False
CHANNELNAME = "dplay"
BASE_URL = "http://es.dplay.com/series/"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.dplay mainlist")
    
    return programas(Item(url="http://es.dplay.com/series/"))

def programas(item):
    logger.info("tvalacarta.channels.dplay programas")

    itemlist = []

    # Download page
    data = scrapertools.cache_page(item.url)
    
    '''
    <div class="b-alphabetical-list__single-show letter-0" data-letter="0">
        <div class="e-grid-show e-grid-show--float">
            <figure class="e-grid-show__container placeholder  ">
                <a href="/dmax/091-alerta-policia/">
                    <img class="e-grid-show__image carousel-image lazy-load" lazy-src="https://eu2-prod-images.disco-api.com/2019/02/14/show-1110-72566123369351.jpg?w=680&f=jpg&p=true&q=75" alt="091 Alerta policía">
                </a>
                <div class="e-grid-show__list-action">
                    <a class="js-e-favorite-handler" data-type='shows' data-uid='1110' data-showslug='091-alerta-policia' data-channelslug='dmax' data-method='POST'>
                        <i class="dplayfont dplayfont-add"></i>
                    </a>
                </div>
                <div class="label-container label-container--show">
                </div>
            </figure>
        </div>
    </div>
    '''

    # Parse programs
    patron  = '<div class="b-alphabetical-list__single-show[^<]+'
    patron += '<div class="e-grid-show e-grid-show--float[^<]+'
    patron += '<figure class="e-grid-show__container[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img class="e-grid-show__image carousel-image lazy-load" lazy-src="([^"]+)" alt="([^"]+)"[^<]+'
    matches = scrapertools.find_multiple_matches(data, patron)

    # Build item list
    for scraped_url, scraped_thumbnail, title in matches:
        url = urlparse.urljoin(item.url,scraped_url)
        # https://eu2-prod-images.disco-api.com/2018/07/12/show-1510-309576665834820.jpg?w=680&f=jpg&p=true&q=75
        thumbnail = scraped_thumbnail.split("?")[0]
        itemlist.append( Item(channel=CHANNELNAME, title=title, action="temporadas", url=url, thumbnail=thumbnail, show=title, folder=True) )

    return itemlist

def detalle_programa(item):

    data = scrapertools.cache_page(item.url)
    item.plot = scrapertools.find_single_match(data, '<meta property="og.description"\s+content="(.*?)"')
    item.thumbnail = scrapertools.find_single_match(data, '<meta property="og.image"\s+content="(.*?)"')

    return item

def temporadas(item):
    logger.info("tvalacarta.channels.dplay temporadas")

    itemlist = []

    # Download page
    data = scrapertools.cache_page(item.url)
    show_id = scrapertools.find_single_match(data,"data-type='shows' data-uid='(\d+)'")

    # Filter only seasons section, for an easier parse
    data = scrapertools.find_single_match(data,'<div class="e-form-dropdown-body">(.*?)</div>')
    
    # Parse seasons
    patron  = '<input type="radio" id="Temporada(\d+)" name="carouselSeasonDropdown" value="([^"]+)">'
    matches = scrapertools.find_multiple_matches(data, patron)
    for season_number,season_label in matches:
        url = "https://es.dplay.com/ajax/carousel/?show_id="+show_id+"&season_number="+season_number+"&count=100&offset=0&cellstyle=type2"
        itemlist.append( Item(channel=CHANNELNAME, title=season_label, action="episodios", url=url, show=item.show, folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.dplay episodios")

    itemlist = []

    data = scrapertools.cache_page(item.url)

    '''
    <div class="carousel-cell">
        <div class="label-container">
            <span class="e-label e-label--top e-label--new">NUEVO</span>
        </div>
        <a href="/dkiss/24-horas-en-urgencias/temporada-13-episodio-11/">
            <div class="e-grid-episode">
                <figure class="e-grid-episode__container ">
                    <div class="e-grid-episode__image-container placeholder">
                        <img class="e-grid-episode__image carousel-image" data-flickity-lazyload="https://eu2-prod-images.disco-api.com/2019/07/19/videoasset-40364-213424951828153.png?w=480&f=jpg&p=true&q=75" alt="24 Horas en urgencias - Episodio 11">
                        <div class="e-grid-episode__image-overlay"></div>
                        <span class="e-grid-episode__date">07/08/2019</span>
                        <span class="e-grid-episode__duration">43 min</span>
                    </div>
                    <figcaption class="e-grid-episode__info">
                        <i class="dplayfont dplayfont-play"></i>
                        <h4 class="e-grid-episode__title">11. Episodio 11</h4>
                        <h5 class="e-grid-episode__description">
                            <span class="e-grid-episode__description-content"></span>
                        </h5>
                    </figcaption>
                </figure>
            </div>
        </a>
    </div>
    '''
    # Parse episodes
    patron  = '<div class="carousel-cell.+?(?=<a)<a href="([^"]+)'
    patron += '.+?(?=data-flickity-lazyload)data-flickity-lazyload="([^"]+)'
    patron += '.+?(?=e-grid-episode__date)e-grid-episode__date">([^<]+)'
    patron += '.+?(?=e-grid-episode__duration)e-grid-episode__duration">(\d+)'
    patron += '.+?(?=e-grid-episode__title)e-grid-episode__title">([^<]+)'
    patron += '.+?(?=e-grid-episode__description-content)e-grid-episode__description-content">([^<]+)?'

    matches = scrapertools.find_multiple_matches(data, patron)

    for scraped_url, scraped_thumbnail, scraped_date, scraped_duration, title, scraped_plot in matches:
        url = urlparse.urljoin(item.url,scraped_url)
        thumbnail = scraped_thumbnail.split("?")[0]
        plot = scrapertools.htmlclean(scraped_plot).strip()
        aired_date = scrapertools.parse_date(scraped_date)
        duration = int(scraped_duration) * 60

        temporada = scrapertools.find_single_match(plot,"E.\d+ T.(\d+)")
        episodio = scrapertools.find_single_match(plot,"E.(\d+) T.\d+")
        if temporada!="" and episodio!="":
            if len(episodio)==1:
                episodio="0"+episodio
            
            title = temporada+"x"+episodio+" "+title

        itemlist.append( Item(channel=CHANNELNAME, title=title, action="play", server="dplay", url=url, thumbnail=thumbnail, plot=plot, aired_date=aired_date, duration=duration, show=item.show, folder=False) )

    return itemlist


def test():
    # Al entrar sale una lista de programas
    menu_items = mainlist(Item())
    if len(menu_items) == 0:
        print("Al entrar a mainlist no sale nada")
        return False

    temporadas_items = temporadas(menu_items[0])
    if len(temporadas_items) == 0:
        print("El programa %s no tiene temporadas" % menu_items[0].title)
        return False

    return True
