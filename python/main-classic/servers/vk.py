# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para VK Server
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def test_video_exists( page_url ):
    logger.info("[uploadedto.py] test_video_exists(page_url='%s')" % page_url)
    
    data = scrapertools.cache_page(page_url)
    if "This video has been removed from public access" in data:
        return False,"El archivo ya no está disponible<br/>en VK (ha sido borrado)"
    else:
        return True,""

# Returns an array of possible video url's from the page_url
def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[vk.py] get_video_url(page_url='%s')" % page_url)

    # Lee la página y extrae el ID del vídeo
    data = scrapertools.cache_page(page_url.replace("amp;",""))
    videourl = ""
    regexp =re.compile(r'vkid=([^\&]+)\&')
    match = regexp.search(data)
    vkid = ""
    if match is not None:
        vkid = match.group(1)
    else:
        data2 = data.replace("\\","")
        patron = '"vkid":"([^"]+)"'
        matches = re.compile(patron,re.DOTALL).findall(data2)
        if len(matches)>0:
            vkid = matches[0]
        else:
            logger.info("no encontro vkid")
    
    logger.info("vkid="+vkid)
    
    # Extrae los parámetros del vídeo y añade las calidades a la lista
    patron  = "var video_host = '([^']+)'.*?"
    patron += "var video_uid = '([^']+)'.*?"
    patron += "var video_vtag = '([^']+)'.*?"
    patron += "var video_no_flv = ([^;]+);.*?"
    patron += "var video_max_hd = '([^']+)'"
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    
    if len(matches)>0:
        #01:44:52 T:2957156352  NOTICE: video_host=http://cs509601.vk.com/, video_uid=149623387, video_vtag=1108941f4c, video_no_flv=1, video_max_hd=1

        video_host = matches[0][0]
        video_uid = matches[0][1]
        video_vtag = matches[0][2]
        video_no_flv = matches[0][3]
        video_max_hd = matches[0][4]
    else:
        #{"uid":"97482389","vid":"161509127\",\"oid\":\"97482389\","host":"507214",\"vtag\":\"99bca9d028\",\"ltag\":\"l_26f55018\",\"vkid\":\"161509127\",\"md_title\":\"El Libro de La Selva - 1967 - tetelx - spanish\",\"md_author\":\"Tetelx Tete\",\"hd\":1,\"no_flv\":1,\"hd_def\":-1,\"dbg_on\":0,\"t\":\"\",\"thumb\":\"http:\\\/\\\/cs507214.vkontakte.ru\\\/u97482389\\\/video\\\/l_26f55018.jpg\",\"hash\":\"3a576695e9f0bfe3093eb21239bd322f\",\"hash2\":\"be750b8971933dd6\",\"is_vk\":\"1\",\"is_ext\":\"0\",\"lang_add\":\"Add to My Videos\",\"lang_share\":\"Share\",\"lang_like\":\"Like\",\"lang_volume_on\":\"Unmute\",\"lang_volume_off\":\"Mute\",\"lang_volume\":\"Volume\",\"lang_hdsd\":\"Change Video Quality\",\"lang_fullscreen\":\"Full Screen\",\"lang_window\":\"Minimize\",\"lang_rotate\":\"Rotate\",\"video_play_hd\":\"Watch in HD\",\"video_stop_loading\":\"Stop Download\",\"video_player_version\":\"VK Video Player\",\"video_player_author\":\"Author - Alexey Kharkov\",\"goto_orig_video\":\"Go to Video\",\"video_get_video_code\":\"Copy vdeo code\",\"video_load_error\":\"The video has not uploaded yet or the server is not available\",\"video_get_current_url\":\"Copy frame link\",\"nologo\":1,\"liked\":0,\"add_hash\":\"67cd39a080ad6e0ad7\",\"added\":1,\"use_p2p\":0,\"p2p_group_id\":\"fb2d8cfdcbea4f3c\"}
        #01:46:05 T:2955558912  NOTICE: video_host=507214, video_uid=97482389, video_vtag=99bca9d028, video_no_flv=1, video_max_hd=1
        data2 = data.replace("\\","")
        video_host = scrapertools.get_match(data2,'"host":"([^"]+)"')
        video_uid = scrapertools.get_match(data2,'"uid":"([^"]+)"')
        video_vtag = scrapertools.get_match(data2,'"vtag":"([^"]+)"')
        video_no_flv = scrapertools.get_match(data2,'"no_flv":([0-9]+)')
        video_max_hd = scrapertools.get_match(data2,'"hd":([0-9]+)')
        
        if not video_host.startswith("http://"):
            video_host = "http://cs"+video_host+".vk.com/"

    logger.info("video_host="+video_host+", video_uid="+video_uid+", video_vtag="+video_vtag+", video_no_flv="+video_no_flv+", video_max_hd="+video_max_hd)

    video_urls = []

    if video_no_flv.strip() == "0" and video_uid != "0":
        tipo = "flv"
        if "http://" in video_host:
            videourl = "%s/u%s/video/%s.%s" % (video_host,video_uid,video_vtag,tipo)
        else:
            videourl = "http://%s/u%s/video/%s.%s" % (video_host,video_uid,video_vtag,tipo)
        
        # Lo añade a la lista
        video_urls.append( ["FLV [vk]",videourl])

    elif video_uid== "0" and vkid != "":     #http://447.gt3.vkadre.ru/assets/videos/2638f17ddd39-75081019.vk.flv 
        tipo = "flv"
        if "http://" in video_host:
            videourl = "%s/assets/videos/%s%s.vk.%s" % (video_host,video_vtag,vkid,tipo)
        else:
            videourl = "http://%s/assets/videos/%s%s.vk.%s" % (video_host,video_vtag,vkid,tipo)
        
        # Lo añade a la lista
        video_urls.append( ["FLV [vk]",videourl])
        
    else:                                   #http://cs12385.vkontakte.ru/u88260894/video/d09802a95b.360.mp4
        #Si la calidad elegida en el setting es HD se reproducira a 480 o 720, caso contrario solo 360, este control es por la xbox
        if video_max_hd=="0":
            video_urls.append( ["240p [vk]",get_mp4_video_link(video_host,video_uid,video_vtag,"240.mp4")])
        elif video_max_hd=="1":
            video_urls.append( ["240p [vk]",get_mp4_video_link(video_host,video_uid,video_vtag,"240.mp4")])
            video_urls.append( ["360p [vk]",get_mp4_video_link(video_host,video_uid,video_vtag,"360.mp4")])
        elif video_max_hd=="2":
            video_urls.append( ["240p [vk]",get_mp4_video_link(video_host,video_uid,video_vtag,"240.mp4")])
            video_urls.append( ["360p [vk]",get_mp4_video_link(video_host,video_uid,video_vtag,"360.mp4")])
            video_urls.append( ["480p [vk]",get_mp4_video_link(video_host,video_uid,video_vtag,"480.mp4")])
        elif video_max_hd=="3":
            video_urls.append( ["240p [vk]",get_mp4_video_link(video_host,video_uid,video_vtag,"240.mp4")])
            video_urls.append( ["360p [vk]",get_mp4_video_link(video_host,video_uid,video_vtag,"360.mp4")])
            video_urls.append( ["480p [vk]",get_mp4_video_link(video_host,video_uid,video_vtag,"480.mp4")])
            video_urls.append( ["720p [vk]",get_mp4_video_link(video_host,video_uid,video_vtag,"720.mp4")])
        else:
            video_urls.append( ["240p [vk]",get_mp4_video_link(video_host,video_uid,video_vtag,"240.mp4")])
            video_urls.append( ["360p [vk]",get_mp4_video_link(video_host,video_uid,video_vtag,"360.mp4")])

    for video_url in video_urls:
        logger.info("[vk.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

def get_mp4_video_link(match0,match1,match2,tipo):
    if match0.endswith("/"):
        videourl = "%su%s/videos/%s.%s" % (match0,match1,match2,tipo)
    else:
        videourl = "%s/u%s/videos/%s.%s" % (match0,match1,match2,tipo)
    return videourl

def find_videos(data):
    encontrados = set()
    devuelve = []

    #http://vkontakte.ru/video_ext.php?oid=95855298&id=162902512&hash=4f0d023887f3648e
    #http://vk.com/video_ext.php?oid=70712020&amp;id=159787030&amp;hash=88899d94685174af&amp;hd=3"
    #http://vk.com/video_ext.php?oid=161288347&#038;id=162474656&#038;hash=3b4e73a2c282f9b4&#038;sd
    #http://vk.com/video_ext.php?oid=146263567&id=163818182&hash=2dafe3b87a4da653&sd
    #http://vk.com/video_ext.php?oid=146263567&id=163818182&hash=2dafe3b87a4da653
    #http://vk.com/video_ext.php?oid=-34450039&id=161977144&hash=0305047ffe3c55a8&hd=3
    data = data.replace("&amp;","&")
    data = data.replace("&#038;","&")
    patronvideos = '(/video_ext.php\?oid=[^&]+&id=[^&]+&hash=[a-z0-9]+)'
    logger.info("[vk.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos).findall(data)

    for match in matches:
        titulo = "[vk]"
        url = "http://vk.com"+match

        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'vk' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    # http://vk.com/video97482389_161509127?section=all
    patronvideos  = '(vk\.[a-z]+\/video[0-9]+_[0-9]+)'
    logger.info("[vk.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    #print data
    for match in matches:
        titulo = "[vk]"
        url = "http://"+match

        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'vk' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve

def test():

    video_urls = get_video_url("http://vk.com/video_ext.php?oid=190230445&id=164616513&hash=ef16fcd83b58b192&hd=1")

    return len(video_urls)>0