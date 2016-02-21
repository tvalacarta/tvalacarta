# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para Yahoo
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import htmlentitydefs
import os

from core import scrapertools
from core import logger
from core import config


# Returns an array of possible video url's from the page_url
def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[yahoo.py] get_video_url(page_url='%s')" % page_url)

    # Lee la página del vídeo
    url= "http://video.yahoo.com/watch/%s" %page_url
    headers = [['User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'],
               ['Referer','http://video.yahoo.com/'],
               ['X-Forwarded-For','12.13.14.15']]
    data = scrapertools.cache_page(url, headers=headers)

    # Retrieve video playlist to extract media URL
    # I'm not completely sure what all these options are, but we
    # seem to need most of them, otherwise the server sends a 401.
    yv_lg = 'R0xx6idZnW2zlrKP8xxAIR'  # not sure what this represents
    yv_bitrate = '700'  # according to Wikipedia this is hard-coded
    url = ('http://cosmos.bcst.yahoo.com/up/yep/process/getPlaylistFOP.php?node_id=' + page_url +
                      '&tech=flash&mode=playlist&lg=' + yv_lg + '&bitrate=' + yv_bitrate + '&vidH=720'+
                  '&vidW=1280'  + '&swf=as3&rd=video.yahoo.com&tk=null&adsupported=v1,v2,&eventid=1301797')

    # Lee la página del vídeo de nuevo
    data2 = scrapertools.cache_page(url, headers=headers)

    # Extract media URL from playlist XML
    mobj = re.search(r'<STREAM APP="(http://.*)" FULLPATH="/?(/.*\.flv\?[^"]*)"', data2)
    if mobj is not None:
        video_url = urllib.unquote(mobj.group(1) + mobj.group(2)).decode('utf-8')
        video_url = re.sub(r'(?u)&(.+?);', htmlentity_transform, video_url)
        logger.info(video_url)
        return video_url        
    else:    
        logger.info('ERROR: Unable to extract media URL http')
        mobj = re.search(r'<STREAM (APP="[^>]+)>', data2)
        if mobj is None:
            logger.info('ERROR: Unable to extract media URL rtmp')
            return ""

        #video_url = mobj.group(1).replace("&amp;","&")
        video_url = urllib.unquote(mobj.group(1).decode('utf-8'))
        video_url = re.sub(r'(?u)&(.+?);', htmlentity_transform, video_url)

        '''
        <STREAM APP="rtmp://s1sflod020.bcst.cdn.s1s.yimg.com/StreamCache" 
        FULLPATH="/s1snfs06r01/001/__S__/lauvpf/76414327.flv?StreamID=76414327&xdata=Njc3Mzc4MzA2NGNiNzI5MW-205754530-0&pl_auth=2598a5574b592b7c6ab262e4775b3930&ht=180&b=eca0lm561k1gn4cb7291a&s=396502118&br=700&q=ahfG2he5gqV40Laz.RUcnB&rd=video.yahoo.com-offsite&so=%2FMUSIC" 
        CLIPID="v205690975" TYPE="STREAMING" AD="NO" 
        APPNAME="ContentMgmt" URLPREFIX="rtmp://" 
        SERVER="s1sflod020.bcst.cdn.s1s.yimg.com" 
        BITRATE="7000" PORT="" 
        PATH="/s1snfs06r01/001/__S__/lauvpf/76414327.flv" 
        QUERYSTRING="StreamID=76414327&xdata=Njc3Mzc4MzA2NGNiNzI5MW-205754530-0&pl_auth=2598a5574b592b7c6ab262e4775b3930&ht=180&b=eca0lm561k1gn4cb7291a&s=396502118&br=700&q=ahfG2he5gqV40Laz.RUcnB&rd=video.yahoo.com-offsite&so=%2FMUSIC" 
        URL="" TITLE="-" AUTHOR="-" COPYRIGHT="(c) Yahoo! Inc. 2006" STARTTIME="" ENDTIME=""/>
        '''

        swfUrl = 'http://d.yimg.com/ht/yep/vyc_player.swf'
        try:
            App         = re.compile(r'APP="([^"]+)"').findall(video_url)[0]
            Fullpath    = re.compile(r'FULLPATH="([^"]+)"').findall(video_url)[0]
            Appname     = re.compile(r'APPNAME="([^"]+)"').findall(video_url)[0]
            #Server      = re.compile(r'SERVER="([^"]+)"').findall(video_url)[0]
            Path        = re.compile(r'PORT=""  PATH="([^"]+)"').findall(video_url)[0].replace(".flv","")
            #Querystring = re.compile(r'QUERYSTRING="([^"]+)"').findall(video_url)[0]
            playpath = Fullpath
            App = App.replace("/StreamCache",":1935/StreamCache/")
            video_url = "%s%s%s playpath=%s swfurl=%s swfvfy=true" %(App,Appname,playpath,Path,swfUrl)
        except:
            logger.info('ERROR: re.compile failed')
            video_url = ""

    logger.info(video_url.encode("utf-8"))
    return video_url

def htmlentity_transform(matchobj):

    """Transforms an HTML entity to a Unicode character.
    This function receives a match object and is intended to be used with
    the re.sub() function.
    """
    entity = matchobj.group(1)

    # Known non-numeric HTML entity
    if entity in htmlentitydefs.name2codepoint:
        return unichr(htmlentitydefs.name2codepoint[entity])

    # Unicode character
    mobj = re.match(ur'(?u)#(x?\d+)', entity)
    if mobj is not None:
        numstr = mobj.group(1)
        if numstr.startswith(u'x'):
            base = 16
            numstr = u'0%s' % numstr
        else:
            base = 10
            
        return unichr(long(numstr, base))

    # Unknown entity in name, return its literal representation
    return (u'&%s;' % entity)
