# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para dplay
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

from core import logger
from core import scrapertools
from core import jsontools

from lib import youtube_dl

import urllib

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.dplay get_video_url(page_url='%s')" % page_url)

    '''
    https://es.dplay.com/dmax/los-ultimos-de-alaska/temporada-1-episodio-8-el-fin-de-la-oscuridad/
    -> <meta itemprop="embedURL" content="https://es.dplay.com/embed/12004/" />

    https://es.dplay.com/ajax/playbackjson/video/12004
    "{\n  \"data\" : {\n    \"id\" : \"12004\",\n    \"type\" : \"videoPlaybackInfo\",\n    \"attributes\" : {\n      \"streaming\" : {\n
    \"hls\" : {\n          \"url\" : \"https://dplayit.akamaized.net/EHD_130642B_DPLAY_SPAIN/0/hls/EHD_130642B_DPLAY_SPAIN.m3u8?hdnts=st=1543695863~exp=1543696163~acl=/*~hmac=2b77b1fc1b4faab4a165d5b4949e95eff4f1f660af1b0f06a577007100b2f5f2&mux_audio=true\"\n        }\n      },\n      \"reportProgressInterval\" : 60000,\n      \"protection\" : {\n        \"schemes\" : {\n          \"clearkey\" : {\n            \"licenseUrl\" : \"https://dplaysouth-vod.akamaized.net/keys/1.clearkey?hdnts=st=1543695863~exp=1543696163~acl=/*~hmac=bc96a190da5be6b57a75a134bf84bc2fd12f2025596e2746953a1d366d6ffeda\"\n          },\n          \"widevine\" : {\n            \"licenseUrl\" : \"https://lic.caas.conax.com/nep/wv/license\"\n          },\n          \"playready\" : {\n            \"licenseUrl\" : \"https://lic.caas.conax.com/nep/pr/cxplayready/rightsmanager.asmx\"\n          },\n          \"fairplay\" : {\n            \"licenseUrl\" : \"https://lic.caas.conax.com/nep/fp/license\",\n            \"certificateUrl\" : \"https://lic.caas.conax.com/nep/fp/certificates/A30BAEFF134A609B019CBBB0D5880803B5D5E9D0\"\n          }\n        },\n        \"key_servers\" : {\n          \"clearkey\" : \"https://dplaysouth-vod.akamaized.net/keys/1.clearkey?hdnts=st=1543695863~exp=1543696163~acl=/*~hmac=bc96a190da5be6b57a75a134bf84bc2fd12f2025596e2746953a1d366d6ffeda\",\n          \"widevine\" : \"https://lic.caas.conax.com/nep/wv/license\",\n          \"playready\" : \"https://lic.caas.conax.com/nep/pr/cxplayready/rightsmanager.asmx\",\n          \"fairplay\" : \"https://lic.caas.conax.com/nep/fp/license\"\n        },\n        \"drm_enabled\" : false,\n        \"clearkey_enabled\" : true,\n        \"drm_token\" : \"\",\n        \"drm_device_id\" : \"\",\n        \"drmEnabled\" : false,\n        \"clearkeyEnabled\" : true,\n        \"drmToken\" : \"\",\n        \"drmDeviceId\" : \"\"\n      },\n      \"viewingHistory\" : {\n        \"viewed\" : true,\n        \"lastStartedTimestamp\" : \"2018-12-01T20:12:01Z\",\n        \"position\" : 300393,\n        \"completed\" : false\n      },\n      \"markers\" : {\n        \"videoAboutToEnd\" : 2639000\n      }\n    }\n  }\n}"
    '''

    data = scrapertools.cache_page(page_url)
    embed_id = scrapertools.find_single_match(data,'<meta itemprop="embedURL" content="https://es.dplay.com/embed/(\d+)/"')
    
    api_url = "https://es.dplay.com/ajax/playbackjson/video/"+embed_id
    data = scrapertools.cache_page(api_url)
    logger.info("data="+data)
    data = data.replace("\\n","\n")
    logger.info("data="+data)
    data = data.replace("\\","")
    logger.info("data="+data)
    data = data[1:-1]
    logger.info("data="+data)

    json_data = jsontools.load_json(data)

    video_urls = []
    video_urls.append( [ "(m3u8)" , json_data["data"]["attributes"]["streaming"]["hls"]["url"] ])

    # Para que ponga la calidad más alta primero
    video_urls.reverse()

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
