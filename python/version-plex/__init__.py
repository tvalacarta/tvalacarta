import sys
import os
import bridge
import channelselector
import re, datetime
from core import config

sys.path.append (os.path.join( config.get_runtime_path(), 'lib' ))

# Passing log and config to an external library
# Credits to https://gist.github.com/mikew/5011984
bridge.init(Log,Prefs,Locale)

from core.item import Item

###################################################################################################

PLUGIN_TITLE     = "tvalacarta"
ART_DEFAULT      = "art-default.jpg"
ICON_DEFAULT     = "icon-default.png"

###################################################################################################
def Start():
    Plugin.AddPrefixHandler("/video/tvalacarta", mainlist, PLUGIN_TITLE, ICON_DEFAULT, ART_DEFAULT)

    '''
    ViewModes = {"List": 65586, "InfoList": 65592, "MediaPreview": 458803, "Showcase": 458810, "Coverflow": 65591,
                 "PanelStream": 131124, "WallStream": 131125, "Songs": 65593, "Seasons": 65593, "Albums": 131123,
                 "Episodes": 65590,"ImageStream":458809,"Pictures":131123}
    '''
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    Plugin.AddViewGroup("MediaPreview", viewMode="MediaPreview", mediaType="items")
    Plugin.AddViewGroup("Showcase", viewMode="Showcase", mediaType="items")
    Plugin.AddViewGroup("Coverflow", viewMode="Coverflow", mediaType="items")
    Plugin.AddViewGroup("PanelStream", viewMode="PanelStream", mediaType="items")
    Plugin.AddViewGroup("WallStream", viewMode="WallStream", mediaType="items")

    ObjectContainer.art        = R(ART_DEFAULT)
    ObjectContainer.title1     = PLUGIN_TITLE
    ObjectContainer.view_group = "InfoList"
    DirectoryObject.thumb      = R(ICON_DEFAULT)

    HTTP.CacheTime = CACHE_1DAY
    HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:10.0.2) Gecko/20100101 Firefox/10.0.2"

####################################################################################################
@handler('/video/tvalacarta', 'Tvalacarta', art=ART_DEFAULT, thumb=ICON_DEFAULT)
def mainlist():
    oc = ObjectContainer(view_group="PanelStream")

    # TODO: Comprueba actualizaciones (hacer genérico core/updater.py)
    HTTP.Request("http://blog.tvalacarta.info/descargas/tvalacarta-version.xml")

    # TODO: Menú completo (da un error extraño al leer el de channelselector.py)
    '''
    itemlist = channelselector.getmainlist()

    for item in itemlist:
        Log.Info("item="+repr(item))
        if item.channel=="configuracion":
            oc.add(PrefsObject(title=item.title,thumb=item.thumbnail))
        elif item.channel=="buscador":
            #oc.add(InputDirectoryObject(key=Callback(buscador),title=item.title,thumb=item.thumbnail,prompt = "Titulo del video"))
        else:
            oc.add(DirectoryObject(key=Callback(canal, channel_name=item.channel, action="mainlist"), title=item.title, thumb="http://media.tvalacarta.info/tvalacarta/squares/"+item.channel+".png"))
    '''
    oc.add(DirectoryObject(key=Callback(channels_list), title="Canales", thumb="http://media.tvalacarta.info/tvalacarta/squares/channels.png"))
    #oc.add(DirectoryObject(key=Callback(channels_list), title=Locale.LocalString("30033"), thumb="http://media.tvalacarta.info/tvalacarta/squares/channelselector.png"))
    #oc.add(InputDirectoryObject(key = Callback(buscador_global), title = 'Buscador', prompt = 'Buscar...', thumb="http://media.tvalacarta.info/tvalacarta/squares/buscador.png"))
    #oc.add(InputDirectoryObject(key = Callback(trailers), title = 'Trailers', prompt = 'Buscar...', thumb="http://media.tvalacarta.info/tvalacarta/squares/trailertools.png"))
    oc.add(PrefsObject(title="Configuracion...",thumb="http://media.tvalacarta.info/tvalacarta/squares/settings.png"))

    return oc

####################################################################################################
@route('/video/tvalacarta/channels_list')
def channels_list():
    oc = ObjectContainer(view_group="PanelStream")

    '''
    oc.add(DirectoryObject(key=Callback(FrontPageList, name="Canales (Todos los idiomas)"), title="Canales (Todos los idiomas)", thumb="http://media.tvalacarta.info/tvalacarta/squares/channelselector.png"))
    oc.add(DirectoryObject(key=Callback(FrontPageList, name="Buscador"), title="Buscador", thumb="http://media.tvalacarta.info/tvalacarta/squares/buscador.png"))
    oc.add(DirectoryObject(key=Callback(ThemeList, name="Favoritos"), title="Favoritos"))
    oc.add(DirectoryObject(key=Callback(ThemeList, name="Descargas"), title="Descargas"))
    oc.add(DirectoryObject(key=Callback(ThemeList, name="Configuración"), title="Configuración"))
    oc.add(DirectoryObject(key=Callback(TagsList, name="Ayuda"), title="Ayuda t"))
    '''

    itemlist = channelselector.channels_list()
    for item in itemlist:
        Log.Info("item="+repr(item))
        if item.type=="generic" and item.channel not in ['tengourl','goear']:
            oc.add(DirectoryObject(key=Callback(canal, channel_name=item.channel, action="mainlist"), title=item.title, thumb="http://media.tvalacarta.info/tvalacarta/squares/"+item.channel+".png"))

    return oc

####################################################################################################
@route('/video/tvalacarta/buscador_global')
def buscador_global(query=""):
    oc = ObjectContainer(view_group="List")

    import buscador
    itemlist = buscador.do_search_results(query)

    for item in itemlist:
        Log.Info("item="+repr(item))
        oc.add(DirectoryObject(key=Callback(canal, channel_name=item.channel, action=item.action, caller_item_serialized=item.serialize()), title=item.title, thumb=item.thumbnail))

    #oc.add(DirectoryObject(key=Callback(channels_list), title=Locale.LocalString("30033"), thumb="http://media.tvalacarta.info/tvalacarta/squares/channelselector.png"))
    return oc

####################################################################################################
@route('/video/tvalacarta/trailers')
def trailers(query=""):
    oc = ObjectContainer(view_group="List")
    oc.add(DirectoryObject(key=Callback(channels_list), title=Locale.LocalString("30033"), thumb="http://media.tvalacarta.info/tvalacarta/squares/channelselector.png"))
    return oc

####################################################################################################
#/{channel_name}/{action}/{caller_item_serialized}
@route('/video/tvalacarta/canal')
def canal(channel_name="",action="",caller_item_serialized=None):
    Log.Info("Entrando en canal para ejectuar "+channel_name+"."+action)
    oc = ObjectContainer(view_group="List")

    try:
        if caller_item_serialized is None:
            Log.Info("caller_item_serialized=None")
            caller_item = Item()
        else:
            Log.Info("caller_item_serialized="+caller_item_serialized)
            caller_item = Item()
            caller_item.fromurl(caller_item_serialized)
        
        Log.Info("caller_item="+str(caller_item))

        Log.Info("Importando...")
        from servers import servertools
        channelmodule = servertools.get_channel_module(channel_name)
        Log.Info("Importado")

        Log.Info("Antes de hasattr")
        if hasattr(channelmodule, action):
            Log.Info("El módulo "+channel_name+" tiene una funcion "+action)
            itemlist = getattr(channelmodule, action)(caller_item)

            if action=="play" and len(itemlist)>0:
                itemlist=play_video(itemlist[0])

        else:
            Log.Info("El módulo "+channel_name+" *NO* tiene una funcion "+action)

            if action=="findvideos":
                Log.Info("Llamando a la funcion findvideos comun")
                itemlist=findvideos(caller_item)
            elif action=="play":
                itemlist=play_video(caller_item)

        Log.Info("Tengo un itemlist con %d elementos" % len(itemlist))

        for item in itemlist:
            try:
                Log.Info("item="+unicode( item.tostring(), "utf-8" , errors="replace" ))
            except:
                pass
            try:
                item.title = unicode( item.title, "utf-8" , errors="replace" )
            except:
                pass
            
            if action!="play":
                cb = Callback(canal, channel_name=channel_name, action=item.action, caller_item_serialized=item.tourl())
                do = DirectoryObject(key=cb, title=item.title, thumb=item.thumbnail)
                oc.add(do)

            else:
                Log.Info("Llamando a la funcion play comun")

                '''
                partObject = PartObject( key = Callback(resuelve, url=item.url) )
                Log.Info("partObject="+str(partObject))
                
                mediaObject = MediaObject( parts = [ partObject ] , container = 'mp4', video_codec = VideoCodec.H264, audio_codec = AudioCodec.AAC )
                Log.Info("mediaObject="+str(mediaObject))

                videoClipObject = VideoClipObject(title=item.title,thumb=item.thumbnail, url=item.url, key=item.url, rating_key=item.url, items = [ mediaObject ] )
                Log.Info("videoClipObject="+str(mediaObject))
                '''

                videoClipObject = VideoClipObject(title=item.title,thumb=item.thumbnail, url="tvalacarta://"+item.url )

                oc.add(videoClipObject)

    except:
        Log.Info("Excepcion al ejecutar "+channel_name+"."+action)
        import traceback
        Log.Info("Detalles: "+traceback.format_exc())

    return oc

def resuelve(url):
    return Redirect(url)

def play_video(item):
    from servers import servertools
    video_urls = servertools.get_video_urls(item.server,item.url)
    itemlist = []
    for video_url in video_urls:
        itemlist.append( Item(channel=item.channel, action="play" , title="Ver el video "+video_url[0] , url=video_url[1], thumbnail=item.thumbnail, plot=item.plot, server=""))

    return itemlist

def findvideos(item):
    from servers import servertools
    return servertools.find_video_items(item=item, channel=item.channel)

#return MessageContainer("Empty", "There aren't any speakers whose name starts with " + char)
#return ObjectContainer(header="Empty", message="There aren't any items")
#oc.add(SearchDirectoryObject(identifier='com.plexapp.plugins.amt', title='Search Trailers', prompt='Search for movie trailer', term=L('Trailers')))