# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para crackle
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys
import simplejson as json

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "crackle"
__category__ = "F"
__type__ = "generic"
__title__ = "crackle"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[crackle.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__ , action="categorias"      , title="Peliculas" , extra = "movies"))
    itemlist.append( Item(channel=__channel__ , action="categorias"      , title="Television", extra = "television"))
    itemlist.append( Item(channel=__channel__ , action="categorias"      , title="Originales" , extra = "originals"))
    itemlist.append( Item(channel=__channel__ , action="categorias"      , title="Colecciones", extra = "collections"))

    return itemlist

def categorias(item):
    logger.info("[crackle.py] categorias")

    itemlist = []
    itemlist.append( Item(channel=__channel__ , action="lista_peliculas"    , title="Todas"          , url="browse"    , extra = item.extra , category="all"))
    itemlist.append( Item(channel=__channel__ , action="lista_peliculas"    , title="Recomendadas"   , url="featured"  , extra = item.extra , category="all"))
    itemlist.append( Item(channel=__channel__ , action="lista_peliculas"    , title="Populares"      , url="popular"   , extra = item.extra , category="all"))
    itemlist.append( Item(channel=__channel__ , action="lista_peliculas"    , title="Recientes"      , url="recent"    , extra = item.extra , category="all"))
    itemlist.append( Item(channel=__channel__ , action="lista_generos"      , title="Generos"        , url=""          , extra = item.extra , category="all"))

    return itemlist
	
def lista_generos(item):
    logger.info("[crackle.py] lista_generos")
#Acao=2, Aventura=4, Drama=5, Animacao=6, Televisao/Animacao/Acao=7, Anime=8, Biografia=12, Comedia=18, Crime=19, 
#Cult=20, Humor Negro=21, Documentario=22, Drama=23, Fantasia=31, Historico=36, Terror=38,
#Artes Marcias=40, Musical=42, Misterio=44, Romance=46, Satira=49, 
#Ficcao=51, Parodia=54, Esportes=55, ( ambiguo ) Suspense/Terror=57, Suspense=58
#Urbano=60, Guerra=61 

    itemlist = []
    itemlist.append( Item(channel=__channel__ , action="lista_peliculas"    , title="Accion"          , url="browse"   , extra = item.extra, category="2" ))
    itemlist.append( Item(channel=__channel__ , action="lista_peliculas"    , title="Aventura"        , url="browse"   , extra = item.extra, category="4"))
    itemlist.append( Item(channel=__channel__ , action="lista_peliculas"    , title="Drama"           , url="browse"   , extra = item.extra, category="5"))
    itemlist.append( Item(channel=__channel__ , action="lista_peliculas"    , title="Animacion"       , url="browse"   , extra = item.extra, category="6"))
    itemlist.append( Item(channel=__channel__ , action="lista_peliculas"    , title="Anime"           , url="browse"   , extra = item.extra, category="12"))
    itemlist.append( Item(channel=__channel__ , action="lista_peliculas"    , title="Biografia"       , url="browse"   , extra = item.extra, category="8"))
    itemlist.append( Item(channel=__channel__ , action="lista_peliculas"    , title="Comedia"         , url="browse"   , extra = item.extra, category="18"))
    itemlist.append( Item(channel=__channel__ , action="lista_peliculas"    , title="Crimen"          , url="browse"   , extra = item.extra, category="19" ))
    itemlist.append( Item(channel=__channel__ , action="lista_peliculas"    , title="Ciencia Ficcion" , url="browse"   , extra = item.extra, category="51" ))
    itemlist.append( Item(channel=__channel__ , action="lista_peliculas"    , title="Suspenso"        , url="browse"   , extra = item.extra, category="58" ))

    return itemlist
	
def lista_peliculas(item):
    logger.info("[crackle.py] lista_peliculas")
	
    #url = build_api_url(item.url, 'movies') 
    url = build_api_url(item.url,item.extra,'full',item.category)


    itemlist = []
    data = scrapertools.cachePage(url)
    logger.info(data)
    mjson = json.loads(data)
    if item.url == 'browse': 
        peliculas = mjson['Entries']
    else:
        peliculas = mjson['Items']        
    peliculas = [pelicula for pelicula in peliculas]
    for pelicula in peliculas:
        title = pelicula['Title'].encode("utf-8")
        url = str(pelicula['ID'])
        url = 'http://android-api-es.crackle.com/Service.svc/' + 'channel/%s/folders/%s?format=json' % (url, 'VE')
        if item.url == 'browse': 
            thumbnail = pelicula['ChannelArtTileWide']
        else:
            thumbnail = pelicula['ImageUrl2']  
        Genre = pelicula['Genre']
        plot = pelicula['Description'].encode("utf-8")
        Mpaa = pelicula['Rating']
        itemlist.append( Item(channel=__channel__, action="lista_videos", title=title , url=url , thumbnail=thumbnail , plot=plot , show=title, extra=item.extra , folder=True) )

    return itemlist

def lista_videos(item):
    logger.info("[crackle.py] lista_videos")
	
    itemlist = []
    data = scrapertools.cachePage(item.url)
    logger.info(data)
    mjson = json.loads(data)
    FolderList = mjson['FolderList']
    FolderList = [folder for folder in FolderList]
    folder = FolderList[0]
    PlaylistList = folder['PlaylistList']
    PlaylistList = [playlist for playlist in PlaylistList]
    #playlist = PlaylistList[0]
    count = 0
    for playlist in PlaylistList:
        MediaList = playlist['MediaList']
        MediaList = [media for media in MediaList]
        for item2 in MediaList:
            title = item2['Title'].encode("utf-8")
            if item.extra=="television":
                count = count + 1
                numero = str(count)
                if count<=9:
                    numero = "0"+numero
                title = numero + " " + title
            HackUrl = item2['Thumbnail_Wide']
            Path = re.compile('http:\\/\\/.+?\/(.+?)_[a-zA-Z0-9]+').findall(HackUrl)[0]
            url = 'http://media-es-am.crackle.com/%s_480p.mp4' % Path
            thumbnail = item2['Thumbnail_Large208x156']
            Genre = item2['Genre']
            plot = item2['Description'].encode("utf-8")
            Mpaa = item2['Rating']
            Duration = item2['Duration']
            itemlist.append( Item(channel=__channel__, action="play", title=title , url=url , thumbnail=thumbnail , fanart=thumbnail, plot=plot , show=item.show, viewmode="movie_with_plot", folder=True) )

    if item.extra=="television" and config.is_xbmc() and len(itemlist)>0:
        itemlist.append( Item(channel=item.channel, title=">> Opciones para esta serie", url=item.url, action="serie_options##lista_videos", thumbnail=item.thumbnail, extra = item.extra , show=item.show, folder=False))

    return itemlist

def build_api_url(list_type,content_type,video_type='all',genres='all',sort='alpha',region='VE',format='json',limit=50,ID=''):
    #LIST TYPES:    browse, popular, recent, details, channel, featured
    #CONTENT TYPES: movies, shows, originals, collections
    #VIDOE TYPES:   all, full, clips, trailers
    #GENRES:        Action_Comedy_Crime_Horror_Sci-Fi_Thriller
	
    base = 'http://android-api-es.crackle.com/Service.svc/'
	
    if list_type == 'browse' or list_type == 'all':
        api_url = base+list_type+'/'+content_type+'/'+video_type+'/'+genres+'/'+sort+'/'+region+'?format='+format
    elif list_type == 'popular' or list_type == 'recent' or list_type == 'featured':
        api_url = base+list_type+'/'+content_type+'/'+video_type+'/'+region+'/'+str(limit)+'?format='+format
    elif list_type == 'channel':
        api_url = base+list_type+'/'+str(ID)+'/folders/'+region+'?format='+format
    elif list_type == 'details':
        #channel or media type
        api_url = base+list_type+'/media/'+str(ID)+'/'+region+'?format='+format
    return api_url

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    
    items_categorias = mainlist(Item())
    items_menu_peliculas = categorias(items_categorias[0])
    items_peliculas = lista_peliculas(items_menu_peliculas[0])
    if len(items_peliculas)==0:
        return False

    items_videos = lista_videos(items_peliculas[0])
    if len(items_videos)==0:
        return False

    return True
