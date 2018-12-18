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
    <div class="b-alphabetical-list__single-show letter-s" data-letter="s">
    <a href="/dkiss/si-quiero-ese-vestido-espana/">
    <div class="e-grid-show e-grid-show--float">
    <figure class="e-grid-show__container placeholder">
    <img class="e-grid-show__image carousel-image lazy-load" lazy-src="https://eu2-prod-images.disco-api.com/2018/10/24/show-2000-9250056697145904.jpg?w=680&f=jpg&p=true&q=75">
    <div class="e-grid-show__list-action">
    <a class="js-e-favorite-handler" data-type='shows' data-uid='2000' data-showslug='' data-channelslug='' data-method='POST'>
    <i class="dplayfont dplayfont-add"></i>
    </a>
    </div>
    </figure>
    </div>
    </a>
    </div>
    '''

    # Parse programs
    patron  = '<div class="b-alphabetical-list__single-show[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<div class="e-grid-show e-grid-show--float"[^<]+'
    patron += '<figure class="e-grid-show__container placeholder"[^<]+'
    patron += '<img class="e-grid-show__image carousel-image lazy-load" lazy-src="([^"]+)"[^<]+'
    patron += '<figcaption class="e-grid-show__info"[^<]+'
    patron += '<h4 class="e-grid-show__title">([^<]+)</h4>'
    matches = scrapertools.find_multiple_matches(data, patron)

    # Build item list
    for scraped_url, scraped_thumbnail, title in matches:
        url = urlparse.urljoin(item.url,scraped_url)
        # https://eu2-prod-images.disco-api.com/2018/07/12/show-1510-309576665834820.jpg?w=680&f=jpg&p=true&q=75
        thumbnail = scraped_thumbnail.split("?")[0]
        itemlist.append( Item(channel=CHANNELNAME, title=title, action="temporadas", url=url, thumbnail=thumbnail, show=title, folder=True) )

    # Parse special programs without title
    patron  = '<div class="b-alphabetical-list__single-show[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<div class="e-grid-show e-grid-show--float"[^<]+'
    patron += '<figure class="e-grid-show__container placeholder"[^<]+'
    patron += '<img class="e-grid-show__image carousel-image lazy-load" lazy-src="([^"]+)"[^<]+'
    patron += '<div class="e-grid-show__list-action">'
    matches = scrapertools.find_multiple_matches(data, patron)

    # Build item list
    for scraped_url, scraped_thumbnail in matches:
        url = urlparse.urljoin(item.url,scraped_url)

        # /dkiss/si-quiero-ese-vestido-espana/
        partes = url.split("/")
        title = partes.pop()
        if title=="":
            title=partes.pop()

        title = title.replace("-"," ").capitalize()

        # https://eu2-prod-images.disco-api.com/2018/07/12/show-1510-309576665834820.jpg?w=680&f=jpg&p=true&q=75
        thumbnail = scraped_thumbnail.split("?")[0]
        itemlist.append( Item(channel=CHANNELNAME, title=title, action="temporadas", url=url, thumbnail=thumbnail, show=title, folder=True) )

        itemlist = sorted(itemlist, key=lambda Item: Item.title)

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

    # Download page
    data = scrapertools.cache_page(item.url)

    '''
    <div class="carousel-cell">

    <a href="/dmax/acuarios-xxl/temporada-5-episodio-14-equipo-de-musica-para-los-chicago-bull/">
    <div class="e-grid-episode">
    <figure class="e-grid-episode__container ">
    <div class="e-grid-episode__image-container placeholder">
    <img class="e-grid-episode__image carousel-image "
    data-flickity-lazyload="https://eu2-prod-images.disco-api.com/2017/09/16/videoasset-16199-1505539939396.jpeg?w=480&f=jpg&p=true&q=75">
    </div>

    <figcaption class="e-grid-episode__info">

    <h4 class="e-grid-episode__title">Equipo de música para los Chicago Bull</h4>
    <h5 class="e-grid-episode__description">
    <span class="e-grid-episode__episode-season">E.14 T.5 - </span>
    <span class="e-grid-episode__episode-descr">PARA TODOS LOS PÚBLICOS. La estrella de los Chicago Bulls, Jimmy Butler, encarga a Wayde y Brett un acuario en forma de radiocasete que se ilumina y del que sale música.</span>
    </h5>

    <span class="e-grid-episode__date">30/06/2016</span>
    <span class="e-grid-episode__duration">44 min&nbsp;&nbsp;
    '''
    # Parse episodes
    patron  = '<div class="carousel-cell"[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<div class="e-grid-episode"[^<]+'
    patron += '<figure class="e-grid-episode__container[^<]+'
    patron += '<div[^<]+'
    patron += '<img class="[^"]+"\s+data-flickity-lazyload="([^"]+)"[^<]+'
    patron += '</div[^<]+'
    patron += '<figcaption class="e-grid-episode__info"[^<]+'
    patron += '<h4 class="e-grid-episode__title">([^<]+)</h4[^<]+'
    patron += '<h5 class="e-grid-episode__description">(.*?)</h5[^<]+'
    patron += '<span class="e-grid-episode__date">([^<]+)</span[^<]+'
    patron += '<span class="e-grid-episode__duration">([^<]+)<'
    matches = scrapertools.find_multiple_matches(data, patron)

    for scraped_url, scraped_thumbnail, title, scraped_plot, scraped_date, scraped_duration in matches:
        url = urlparse.urljoin(item.url,scraped_url)
        # https://eu2-prod-images.disco-api.com/2018/07/12/show-1510-309576665834820.jpg?w=680&f=jpg&p=true&q=75
        thumbnail = scraped_thumbnail.split("?")[0]
        plot = scrapertools.htmlclean(scraped_plot).strip()
        plot = re.compile("\s+",re.DOTALL).sub(" ",plot)
        aired_date = scrapertools.parse_date(scraped_date)
        duration = scrapertools.htmlclean(scraped_duration).strip()

        temporada = scrapertools.find_single_match(plot,"E.\d+ T.(\d+)")
        episodio = scrapertools.find_single_match(plot,"E.(\d+) T.\d+")
        if temporada!="" and episodio!="":
            if len(episodio)==1:
                episodio="0"+episodio
            
            title = temporada+"x"+episodio+" "+title

        itemlist.append( Item(channel=CHANNELNAME, title=title, action="play", server="dplay", url=url, thumbnail=thumbnail, plot=plot, aired_date=aired_date, duration=duration, show=item.show, folder=False) )

    return itemlist
