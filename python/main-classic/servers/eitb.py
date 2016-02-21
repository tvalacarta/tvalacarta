# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para eitb
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

import pyamf
from pyamf import remoting
import httplib, socket

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("[eitb.py] get_video_url(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)

    #<param name="playerID" value="893448935001" />
    #<param name="playerKey" value="AQ~~,AAAAF8Q-iyk~,FDoJSqZe3TSVeJrw8hVEauWQtrf-1uI7" />
    player_id = scrapertools.get_match(data,'<param name="playerID" value="(\d+)')
    logger.info("player_id="+player_id)

    player_key = scrapertools.get_match(data,'<param name="playerKey" value="([^"]+)"')
    logger.info("player_key="+player_key)

    # id del contenido, viene en la URL
    # http://www.eitb.tv/es/#/video/1628880837001
    video_player = scrapertools.get_match(page_url,'http://www.eitb.tv/es/#/video/(\d+)')
    logger.info("video_player="+video_player)

    response = get_rtmp( player_key , video_player , page_url , player_id)

    string_response = str(response)
    logger.info("response="+string_response)
    full_url = scrapertools.get_match(string_response,"'FLVFullLengthURL'\: u'([^']+)'")
    logger.info("full_url="+full_url)

    #rtmp://cp150446.edgefcs.net/ondemand/&mp4:102076681001/102076681001_1628893264001_75044-20120509-033240.mp4?__nn__=1497926354001&slist=102076681001/&auth=daEceaYdNdUayaSc4bicnc0dEcOc7cUdxco-bqZWLa-bWG-olxDAsxw_yEzs_IEyA_GmD&aifp=bcosuds
    #rtmp://brightcove.fcod.llnwd.net/a500/e1/uds/rtmp/ondemand/&mp4:102076681001/102076681001_734052664001_3997-20101231-164923.mp4&1355767200000&d7c4282069a19fa7735359ea088c3c42
    '''
    [truncated] Property 'app' String 'ondemand?__nn__=1497926354001&slist=102076681001/&auth=daEceaYdNdUayaSc4bicnc0dEcOc7cUdxco-bqZWLa-bWG-olxDAsxw_yEzs_IEyA_GmD&aifp=bcosuds&videoId=1628880837001&lineUpId=&pubId=102076681001&playerId=893448
    Property 'swfUrl' String 'http://admin.brightcove.com/viewer/us20121213.1025/federatedVideoUI/BrightcovePlayer.swf?uid=1355746343102'
    [truncated] Property 'tcUrl' String 'rtmp://cp150446.edgefcs.net:1935/ondemand?__nn__=1497926354001&slist=102076681001/&auth=daEceaYdNdUayaSc4bicnc0dEcOc7cUdxco-bqZWLa-bWG-olxDAsxw_yEzs_IEyA_GmD&aifp=bcosuds&videoId=1628880837001&lineUpId=
    Property 'pageUrl' String 'http://www.eitb.tv/es/#/video/1628880837001'
    [truncated] String 'mp4:102076681001/102076681001_1628893296001_75044-20120509-033240.mp4?__nn__=1497926354001&slist=102076681001/&auth=daEceaYdNdUayaSc4bicnc0dEcOc7cUdxco-bqZWLa-bWG-olxDAsxw_yEzs_IEyA_GmD&aifp=bcosuds&videoId=162888083700
    '''
    
    #rtmp_url = scrapertools.get_match(video_url,"(rtmp\://[^\/]+/)")
    pubId = scrapertools.get_match(full_url,"slist\=(\d+)")
    logger.info("pubId="+pubId)
    
    app = "ondemand?"+scrapertools.get_match(full_url,"\?(.*?)$")+"&videoId="+video_player+"&lineUpId=&pubId=102076681001&playerId="+player_id
    logger.info("app="+app)
    
    playpath = scrapertools.get_match(full_url,"(mp4\:.*?)$")+"&videoId="+video_player
    logger.info("playpath="+playpath)
    
    swfurl = "http://admin.brightcove.com/viewer/us20121213.1025/federatedVideoUI/BrightcovePlayer.swf?uid=1355746343102"
    logger.info("swfurl="+swfurl)
    
    pageurl = page_url
    logger.info("pageurl="+pageurl)

    '''
    13:47:17 T:2953318400  NOTICE: pubId=102076681001
    13:47:17 T:2953318400  NOTICE: app=ondemand__nn__=1497926354001&slist=102076681001/&auth=daEceaYdNdUayaSc4bicnc0dEcOc7cUdxco-bqZWLa-bWG-olxDAsxw_yEzs_IEyA_GmD&aifp=bcosuds&videoId=1628880837001&lineUpId=&pubId=102076681001&playerId=893448935001
    13:47:17 T:2953318400  NOTICE: playpath=mp4:102076681001/102076681001_1628893264001_75044-20120509-033240.mp4?__nn__=1497926354001&slist=102076681001/&auth=daEceaYdNdUayaSc4bicnc0dEcOc7cUdxco-bqZWLa-bWG-olxDAsxw_yEzs_IEyA_GmD&aifp=bcosuds&videoId=1628880837001
    13:47:17 T:2953318400  NOTICE: swfurl=http://admin.brightcove.com/viewer/us20121213.1025/federatedVideoUI/BrightcovePlayer.swf?uid=1355746343102
    13:47:17 T:2953318400  NOTICE: pageurl=http://www.eitb.tv/es/#/video/1628880837001
    13:47:17 T:2953318400  NOTICE: url=rtmp://cp150446.edgefcs.net/ondemand/&mp4:102076681001/102076681001_1628893264001_75044-20120509-033240.mp4?__nn__=1497926354001&slist=102076681001/&auth=daEceaYdNdUayaSc4bicnc0dEcOc7cUdxco-bqZWLa-bWG-olxDAsxw_yEzs_IEyA_GmD&aifp=bcosuds app=ondemand__nn__=1497926354001&slist=102076681001/&auth=daEceaYdNdUayaSc4bicnc0dEcOc7cUdxco-bqZWLa-bWG-olxDAsxw_yEzs_IEyA_GmD&aifp=bcosuds&videoId=1628880837001&lineUpId=&pubId=102076681001&playerId=893448935001 swfUrl=http://admin.brightcove.com/viewer/us20121213.1025/federatedVideoUI/BrightcovePlayer.swf?uid=1355746343102 playpath=mp4:102076681001/102076681001_1628893264001_75044-20120509-033240.mp4?__nn__=1497926354001&slist=102076681001/&auth=daEceaYdNdUayaSc4bicnc0dEcOc7cUdxco-bqZWLa-bWG-olxDAsxw_yEzs_IEyA_GmD&aifp=bcosuds&videoId=1628880837001
    13:47:17 T:2953318400  NOTICE: [cartoonito.py] RTMP [brightcove] - rtmp://cp150446.edgefcs.net/ondemand/&mp4:102076681001/102076681001_1628893264001_75044-20120509-033240.mp4?__nn__=1497926354001&slist=102076681001/&auth=daEceaYdNdUayaSc4bicnc0dEcOc7cUdxco-bqZWLa-bWG-olxDAsxw_yEzs_IEyA_GmD&aifp=bcosuds app=ondemand__nn__=1497926354001&slist=102076681001/&auth=daEceaYdNdUayaSc4bicnc0dEcOc7cUdxco-bqZWLa-bWG-olxDAsxw_yEzs_IEyA_GmD&aifp=bcosuds&videoId=1628880837001&lineUpId=&pubId=102076681001&playerId=893448935001 swfUrl=http://admin.brightcove.com/viewer/us20121213.1025/federatedVideoUI/BrightcovePlayer.swf?uid=1355746343102 playpath=mp4:102076681001/102076681001_1628893264001_75044-20120509-033240.mp4?__nn__=1497926354001&slist=102076681001/&auth=daEceaYdNdUayaSc4bicnc0dEcOc7cUdxco-bqZWLa-bWG-olxDAsxw_yEzs_IEyA_GmD&aifp=bcosuds&videoId=1628880837001
    '''

    url=full_url + " app=" + app + " swfUrl=" + swfurl + " playpath=" + playpath + " pageUrl="+pageurl
    logger.info("url="+url)
    
    video_urls = []
    video_urls.append( [ "RTMP [eitb]" , url ] )

    for video_url in video_urls:
        logger.info("[eitb.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

def get_rtmp(key, content_id, url, exp_id):
   conn = httplib.HTTPConnection("c.brightcove.com")
   envelope = build_amf_request(key, content_id, url, exp_id)
   logger.info("REQUEST="+str(envelope))
   encoded = remoting.encode(envelope)
   logger.info("encoded="+str(encoded))
   stringenvelope=str(encoded.read())
   logger.info("stringenvelope="+stringenvelope)
   conn.request("POST", "/services/messagebroker/amf?playerKey="+key, stringenvelope,{'content-type': 'application/x-amf'})
   response = conn.getresponse().read()
   logger.info("RESPONSE="+str(response))
   response = remoting.decode(response).bodies[0][1].body
   logger.info("RESPONSE="+str(response))
   return response

class ViewerExperienceRequest(object):
   def __init__(self, URL, contentOverrides, experienceId, playerKey, TTLToken=''):
      self.TTLToken = TTLToken
      self.URL = URL
      self.deliveryType = float(0)
      self.contentOverrides = contentOverrides
      self.experienceId = experienceId
      self.playerKey = playerKey

class ContentOverride(object):
   def __init__(self, contentId, contentType=0, target='videoPlayer'):
      self.contentType = contentType
      self.contentId = contentId
      self.target = target
      self.contentIds = None
      self.contentRefId = None
      self.contentRefIds = None
      self.contentType = 0
      self.featureId = float(0)
      self.featuredRefId = None

def build_amf_request(key, content_id, url, exp_id):
   print 'ContentId:'+content_id
   print 'ExperienceId:'+exp_id
   print 'URL:'+url

   const = '40421d54b4cdb3e933cb99efe6c41f9ef5acff82'
   pyamf.register_class(ViewerExperienceRequest, 'com.brightcove.experience.ViewerExperienceRequest')
   pyamf.register_class(ContentOverride, 'com.brightcove.experience.ContentOverride')
   content_override = ContentOverride(int(content_id))
   viewer_exp_req = ViewerExperienceRequest(url, [content_override], int(exp_id), key)

   env = remoting.Envelope(amfVersion=3)
   env.bodies.append(
      (
         "/1",
         remoting.Request(
            target="com.brightcove.experience.ExperienceRuntimeFacade.getDataForExperience",
            body=[const, viewer_exp_req],
            envelope=env
         )
      )
   )
   return env

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
