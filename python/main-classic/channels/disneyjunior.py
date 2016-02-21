# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Canal para Disney Junior
#---------------------------------------------------------------------------
import os
import sys

import urlparse,re
import urllib
import datetime

from core import logger
from core import config
from core import scrapertools
from core.item import Item

import youtube_channel

DEBUG = True
CHANNELNAME = "disneyjunior"

def isGeneric():
    return True

# Entry point
def mainlist(item):
    logger.info("disneyjunior.main_list")
    itemlist=[]

    #itemlist.append( Item(channel=CHANNELNAME, title="Web oficial" , action="disneyweb" , url="http://www.disney.es/disney-junior/contenido/video.jsp", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Canal YouTube (ES)" , action="youtube_playlists" , url="DisneyJuniorES", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Canal YouTube (LA)" , action="youtube_playlists" , url="DisneyJuniorLA", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Canal YouTube (UK)" , action="youtube_playlists" , url="DisneyJuniorUK", folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Canal YouTube (FR)" , action="youtube_playlists" , url="DisneyJuniorFR", folder=True) )

    return itemlist

# Show all videos from the official website
def disneyweb(item):
    logger.info("disneyjunior.disneyweb")
    itemlist=[]

    # Fetch video list page
    data = scrapertools.cache_page( item.url )
    logger.info("data="+data)
    data = scrapertools.find_single_match( data , '<div id="video_main_promos_inner">(.*?)<div id="content_index_navigation">')
    
    # Extract items
    '''
    <div class="promo" style="background-image: url(/cms_res/disney-junior/images/promo_support/promo_holders/video.png);">
    <a href="/disney-junior/contenido/video.jsp?v=01-manny-manitas-cuenta" class="refreshSelectedView unprocessed" data-itemName="01-manny-manitas-cuenta">
    <img src="/cms_res/disney-junior/images/video/cuenta_con_mannyPV08604_164x104.jpg" class="promo_image" alt=""/>
    </a>
    <div class="promo_playing_mask"></div>
    <div class="promo_playing_maskCopy"><p>Estás viendo</p></div>
    <div class="promo_title_3row"><p>Cuenta con Manny: Contando tacos de pared</p></div>
    <a class="playlist_button"  href="#" data-itemName="01-manny-manitas-cuenta"><img src="/cms_res/disney-junior/images/promo_support/playlist_add_icon.png" alt="" /></a>
    </div>
    '''
    pattern  = '<div class="promo"[^<]+'
    pattern += '<a href="([^"]+)"[^<]+'
    pattern += '<img src="([^"]+)"[^<]+'
    pattern += '</a[^<]+'
    pattern += '<div[^<]+</div[^<]+'
    pattern += '<div[^<]+<p[^<]+</p[^<]+</div[^<]+'
    pattern += '<div[^<]+<p>([^<]+)</p>'
    matches = re.compile(pattern,re.DOTALL).findall(data)
    
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        # Not the better way to parse XML, but clean and easy
        title = scrapedtitle
        thumbnail = urlparse.urljoin( item.url , scrapedthumbnail )
        url = urlparse.urljoin( item.url , scrapedurl.strip() )
        plot = ""

        # Appends a new item to the xbmc item list
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="play" , url=url, thumbnail=thumbnail, plot=plot , folder=False) )

    return itemlist

# Play one video from the official website
def play(item):
    logger.info("disneyjunior.disneyweb_play ")
    itemlist=[]

    if "disney.es" in item.url:

        # Obtiene el id del video
        page_id = scrapertools.get_match( item.url , "/disney-junior/contenido/video.jsp\?v=([a-z0-9\-\_]+)" )

        # Fetch page
        data = scrapertools.cache_page( item.url )

        #"urlId":"01-manny-manitas-cuenta","pageTitle":"Disney Junior | Videos - Manny Manitas - Contando tacos de pared","description":"Cuenta con Manny: Contando tacos de pared",
        #"thumbnailImage":"","media":{"stream":{"program":"cuenta_con_mannyPV08604.mp4","server":"rtmpe://cp121902.edgefcs.net/ondemand/"},
        #"progressive":"http://www.disney.es:80/cms_res/disney-junior/video/cuenta_con_mannyPV08604.mp4"}},{"thumbnailAlt":"","title":"Canta con DJ: Senderismo","analyticsAssetName":"vid:djr:hdm:canta_dj_senderismo_mannyHV13750.mp4","urlId":"02-canta_con_dj_senderismo","pageTitle":"Canta con_dj_senderismo |  Video | Di
        url = scrapertools.get_match( data , '"urlId"\:"'+page_id+'","pageTitle"\:"[^"]+","description":"[^"]+","thumbnailImage":"","media":{"stream":{"program":"[^"]+","server":"[^"]+"},"progressive":"([^"]+)"}}' )
        logger.info("disneyjunior.disneyweb_play url="+url)

        itemlist.append( Item(channel=CHANNELNAME, title=item.title , action="play" , url=url, folder=False) )
    else:
        itemlist.append(item)
    
    return itemlist

# Show all YouTube playlists for the selected channel
def youtube_playlists(item):
    return youtube_channel.playlists(item,item.url)

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    items_mainlist = mainlist(Item())
    
    items_programas = disneyweb(items_mainlist[0])
    if len(items_programas)==0:
        return False

    items_videos = play(items_programas[0])
    if len(items_videos)==0:
        return False

    for youtube_item in items_mainlist[1:]:
        items_videos = youtube_videos(youtube_item)
        if len(items_videos)==0:
            return False

    return bien