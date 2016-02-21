# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para TNU (Uruguay)
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re,os,datetime
import urllib
import base64

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from core import jsontools

DEBUG = False
CHANNELNAME = "tnu"

def isGeneric():
    return True

def get_main_page():

    file_name = os.path.join( config.get_data_path() , "tnu.cached" )
    logger.info("tvalacarta.channels.tnu get_main_page file_name="+file_name)

    if not os.path.exists(file_name):
        logger.info("tvalacarta.channels.tnu get_main_page no existe")
        data = scrapertools.cachePage("http://www.tnu.com.uy/videoteca/")
        f = open(file_name,"w")
        f.write(data)
        f.close()
        return data

    # Calcula la antiguedad del fichero
    file_timestap = os.path.getmtime(file_name)
    file_datetime = datetime.datetime.fromtimestamp(file_timestap)
    now_datetime = datetime.datetime.now()

    # Si tiene más de 3 horas
    diferencia = (now_datetime - file_datetime).seconds

    if diferencia > 60*60*3:
        logger.info("tvalacarta.channels.tnu get_main_page tiene más de 3 horas, lee de nuevo y actualiza la cache")
        data = scrapertools.cachePage("http://www.tnu.com.uy/videoteca/")
        f = open(file_name,"w")
        f.write(data)
        f.close()
        return data
    else:
        logger.info("tvalacarta.channels.tnu get_main_page tiene menos de 3 horas, devuelve la cache")
        f = open(file_name,"r")
        data = f.read()
        f.close()
        return data

def mainlist(item):
    logger.info("tvalacarta.channels.tnu mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Últimos vídeos añadidos" , url="http://www.tnu.com.uy/scripts/filtrarVideoteca.php?orden=fecha_desc" , action="episodios" , folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Todos los programas" , url="http://www.tnu.com.uy/videoteca/" , action="programas" , folder=True) )
    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.tnu programas")
    itemlist = []

    # Extrae las series
    data = get_main_page()
    data = scrapertools.find_single_match(data,"window.PROGRAMAS\s+\=\s+jQuery.parseJSON\('(.*?\}\])'\)\;")
    #logger.info("tvalacarta.channels.tnu data="+data)

    json_object = jsontools.load_json(data)
    #logger.info("tvalacarta.channels.tnu json_object="+repr(json_object))
    
    for json_item in json_object:
        num_videos = len(json_item["videos"])
        if num_videos>0:
            title = base64.b64decode(json_item["titulo"]).strip()
            thumbnail = ""
            plot = ""
            url = "http://www.tnu.com.uy/scripts/filtrarVideoteca.php?programa="+repr(json_item["id"])+"&orden=fecha_desc"
            if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
            itemlist.append( Item( channel=item.channel , title=title , action="episodios" , url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=True ) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.tnu episodios")
    itemlist=[]

    # Extrae los episodios

    #http://www.tnu.com.uy/scripts/filtrarVideoteca.php?orden=fecha_desc
    #http://www.tnu.com.uy/scripts/filtrarVideoteca.php?offset=60&orden=fecha_desc
    #http://www.tnu.com.uy/scripts/filtrarVideoteca.php?programa=4872&orden=fecha_desc
    
    '''
    {"errorCode":0,"errorMsg":"SUCCESS","info":
        [
            {
                "fecha":1385383871,
                "fecha_formated":"25 de Noviembre de 2013",
                "id":5278,
                "titulo":"Vampiros &#038; murci\u00e9lagos",
                "uniqueTitle":"vampiros-murcielagos",
                "foto":"http:\/\/www.tnu.com.uy\/content\/resize?image=aHR0cDovL2kueXRpbWcuY29tL3ZpLzhNZW5vUnNHd0g4LzAuanBn&new_width=190&new_height=100&crop=1&sec=MTkwMTAwaHR0cDovL2kueXRpbWcuY29tL3ZpLzhNZW5vUnNHd0g4LzAuanBnMXRlbnNhaUF0M240NQ==&pathResize=L2hvbWUvdG51Y29tL3B1YmxpY19odG1sL2NvbnRlbnQvd3AtY29udGVudC91cGxvYWRzL3Jlc2l6ZS8=&httpResize=aHR0cDovL3RudS5jb20udXkvY29udGVudC93cC1jb250ZW50L3VwbG9hZHMvcmVzaXplLw=="},
            {"fecha":1384772387,"fecha_formated":"18 de Noviembre de 2013","id":5227,"titulo":"Le\u00f3n marino","uniqueTitle":"leon-marino","foto":"http:\/\/www.tnu.com.uy\/content\/resize?image=aHR0cDovL2kueXRpbWcuY29tL3ZpL21ZZEFxb2RIUW9VLzAuanBn&new_width=190&new_height=100&crop=1&sec=MTkwMTAwaHR0cDovL2kueXRpbWcuY29tL3ZpL21ZZEFxb2RIUW9VLzAuanBnMXRlbnNhaUF0M240NQ==&pathResize=L2hvbWUvdG51Y29tL3B1YmxpY19odG1sL2NvbnRlbnQvd3AtY29udGVudC91cGxvYWRzL3Jlc2l6ZS8=&httpResize=aHR0cDovL3RudS5jb20udXkvY29udGVudC93cC1jb250ZW50L3VwbG9hZHMvcmVzaXplLw=="},{"fecha":1384171970,"fecha_formated":"11 de Noviembre de 2013","id":5177,"titulo":"Cardenal amarillo","uniqueTitle":"cardenal-amarillo","foto":"http:\/\/www.tnu.com.uy\/content\/resize?image=aHR0cDovL2kueXRpbWcuY29tL3ZpL1o4TWJhS2d3UVF3LzAuanBn&new_width=190&new_height=100&crop=1&sec=MTkwMTAwaHR0cDovL2kueXRpbWcuY29tL3ZpL1o4TWJhS2d3UVF3LzAuanBnMXRlbnNhaUF0M240NQ==&pathResize=L2hvbWUvdG51Y29tL3B1YmxpY19odG1sL2NvbnRlbnQvd3AtY29udGVudC91cGxvYWRzL3Jlc2l6ZS8=&httpResize=aHR0cDovL3RudS5jb20udXkvY29udGVudC93cC1jb250ZW50L3VwbG9hZHMvcmVzaXplLw=="},{"fecha":1383588999,"fecha_formated":"4 de Noviembre de 2013","id":5136,"titulo":"Yacar\u00e9","uniqueTitle":"yacare","foto":"http:\/\/www.tnu.com.uy\/content\/resize?image=aHR0cDovL2kueXRpbWcuY29tL3ZpL1QyS3VtX0luSnY4LzAuanBn&new_width=190&new_height=100&crop=1&sec=MTkwMTAwaHR0cDovL2kueXRpbWcuY29tL3ZpL1QyS3VtX0luSnY4LzAuanBnMXRlbnNhaUF0M240NQ==&pathResize=L2hvbWUvdG51Y29tL3B1YmxpY19odG1sL2NvbnRlbnQvd3AtY29udGVudC91cGxvYWRzL3Jlc2l6ZS8=&httpResize=aHR0cDovL3RudS5jb20udXkvY29udGVudC93cC1jb250ZW50L3VwbG9hZHMvcmVzaXplLw=="},{"fecha":1383134263,"fecha_formated":"30 de Octubre de 2013","id":5109,"titulo":"Tar\u00e1ntula","uniqueTitle":"tarantula-2","foto":"http:\/\/www.tnu.com.uy\/content\/resize?image=aHR0cDovL2kueXRpbWcuY29tL3ZpL3R5QzVBRHg3V09ZLzAuanBn&new_width=190&new_height=100&crop=1&sec=MTkwMTAwaHR0cDovL2kueXRpbWcuY29tL3ZpL3R5QzVBRHg3V09ZLzAuanBnMXRlbnNhaUF0M240NQ==&pathResize=L2hvbWUvdG51Y29tL3B1YmxpY19odG1sL2NvbnRlbnQvd3AtY29udGVudC91cGxvYWRzL3Jlc2l6ZS8=&httpResize=aHR0cDovL3RudS5jb20udXkvY29udGVudC93cC1jb250ZW50L3VwbG9hZHMvcmVzaXplLw=="},{"fecha":1382536216,"fecha_formated":"23 de Octubre de 2013","id":5065,"titulo":"Venado de campo","uniqueTitle":"venado-de-campo","foto":"http:\/\/www.tnu.com.uy\/content\/resize?image=aHR0cDovL2kueXRpbWcuY29tL3ZpL0xQUzJTc1YzRExFLzAuanBn&new_width=190&new_height=100&crop=1&sec=MTkwMTAwaHR0cDovL2kueXRpbWcuY29tL3ZpL0xQUzJTc1YzRExFLzAuanBnMXRlbnNhaUF0M240NQ==&pathResize=L2hvbWUvdG51Y29tL3B1YmxpY19odG1sL2NvbnRlbnQvd3AtY29udGVudC91cGxvYWRzL3Jlc2l6ZS8=&httpResize=aHR0cDovL3RudS5jb20udXkvY29udGVudC93cC1jb250ZW50L3VwbG9hZHMvcmVzaXplLw=="},{"fecha":1382102822,"fecha_formated":"18 de Octubre de 2013","id":5024,"titulo":"Chorlo canela","uniqueTitle":"chorlo-canela","foto":"http:\/\/www.tnu.com.uy\/content\/resize?image=aHR0cDovL2kueXRpbWcuY29tL3ZpL3MtSGlIdm9LeGNFLzAuanBn&new_width=190&new_height=100&crop=1&sec=MTkwMTAwaHR0cDovL2kueXRpbWcuY29tL3ZpL3MtSGlIdm9LeGNFLzAuanBnMXRlbnNhaUF0M240NQ==&pathResize=L2hvbWUvdG51Y29tL3B1YmxpY19odG1sL2NvbnRlbnQvd3AtY29udGVudC91cGxvYWRzL3Jlc2l6ZS8=&httpResize=aHR0cDovL3RudS5jb20udXkvY29udGVudC93cC1jb250ZW50L3VwbG9hZHMvcmVzaXplLw=="},{"fecha":1382102636,"fecha_formated":"18 de Octubre de 2013","id":5023,"titulo":"Tortuga verde","uniqueTitle":"tortuga-verde","foto":"http:\/\/www.tnu.com.uy\/content\/resize?image=aHR0cDovL2kueXRpbWcuY29tL3ZpL016bUdMM2NZSkpnLzAuanBn&new_width=190&new_height=100&crop=1&sec=MTkwMTAwaHR0cDovL2kueXRpbWcuY29tL3ZpL016bUdMM2NZSkpnLzAuanBnMXRlbnNhaUF0M240NQ==&pathResize=L2hvbWUvdG51Y29tL3B1YmxpY19odG1sL2NvbnRlbnQvd3AtY29udGVudC91cGxvYWRzL3Jlc2l6ZS8=&httpResize=aHR0cDovL3RudS5jb20udXkvY29udGVudC93cC1jb250ZW50L3VwbG9hZHMvcmVzaXplLw=="}]}
    '''
    data = scrapertools.cachePage( item.url )
    all_data = get_main_page()
    #logger.info("tvalacarta.channels.tnu all_data="+all_data)

    json_object = jsontools.load_json(data)
    #logger.info("tvalacarta.channels.tnu json_object="+repr(json_object))
    
    for json_item in json_object["info"]:
        title = json_item["titulo"].strip()+" ("+json_item["fecha_formated"].strip()+")"
        thumbnail = base64.b64decode( scrapertools.find_single_match( json_item["foto"] , "image\=([^\&]+)" ) )
        
        #"id":7925,"titulo":"UG9yIGxvcyBiYXJyaW9z","descripcion":"UmVjb3JyaW1vcyBkaXN0aW50b3MgYmFycmlvcyBkZSBNb250ZXZpZGVvLCBlbnNheW9zIGRlIHBhcm9kaXN0YXMsIG11cmdhcyB5IGx1Ym9sb3Mu","embed":"PGlmcmFtZSB3aWR0aD0nNTc0JyBoZWlnaHQ9JzMxNScgc3JjPSJodHRwOi8vd3d3LnlvdXR1YmUuY29tL2VtYmVkL0s2Nlc2Y01jTUxVP2F1dG9wbGF5PTEiIGZyYW1lYm9yZGVyPSIwIiBhbGxvd2Z1bGxzY3JlZW4+PC9pZnJhbWU+","imgCompartir":"aHR0cDovL2kueXRpbWcuY29tL3ZpL0s2Nlc2Y01jTUxVLzAuanBn","foto":"Y29udGVudC9yZXNpemU\/aW1hZ2U9YUhSMGNEb3ZMMmt1ZVhScGJXY3VZMjl0TDNacEwwczJObGMyWTAxalRVeFZMekF1YW5CbiZuZXdfd2lkdGg9MTkwJm5ld19oZWlnaHQ9MTAwJmNyb3A9MSZzZWM9TVRrd01UQXdhSFIwY0Rvdkwya3VlWFJwYldjdVkyOXRMM1pwTDBzMk5sYzJZMDFqVFV4Vkx6QXVhbkJuTVhSbGJuTmhhVUYwTTI0ME5RPT0mcGF0aFJlc2l6ZT1MMmh2YldVdmRHNTFZMjl0TDNCMVlteHBZMTlvZEcxc0wyTnZiblJsYm5RdmQzQXRZMjl1ZEdWdWRDOTFjR3h2WVdSekwzSmxjMmw2WlM4PSZodHRwUmVzaXplPWFIUjBjRG92TDNSdWRTNWpiMjB1ZFhrdlkyOXVkR1Z1ZEM5M2NDMWpiMjUwWlc1MEwzVndiRzloWkhNdmNtVnphWHBsTHc9PQ==","uniqueTitle":"cG9yLWxvcy1iYXJyaW9z","uniqueTitleProgram":"c2FsdS1jYXJuYXZhbA==","fecha":1420412392,"programa_id":"2396"},{"id":7923,"titulo":"RW4gZG9zIHBhbmVz","descripcion":"Q2ljbG8gZXNwZWNpYWwgZGUgU2Fsw7ogQ2FybmF2YWwgY29uIGxhcyBhY3R1YWNpb25lcyBlbiBlbCBUZWF0cm8gZGUgVmVyYW5vLg==","embed":"PGlmcmFtZSB3aWR0a
        plot = scrapertools.find_single_match(all_data,'"id"\:'+str(json_item["id"])+',"titulo"\:"[^"]*","descripcion":"([^"]*)"')
        plot = base64.b64decode(plot)        
        #url = str(json_item["id"])
        url = scrapertools.find_single_match(all_data,'"id"\:'+str(json_item["id"])+',"titulo":"[^"]*","descripcion":"[^"]*","embed":"([^"]+)"')
        url = base64.b64decode(url)    
        url = scrapertools.find_single_match(url,'youtube.com/embed/([A-Za-z0-9_-]+)')

        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="play" , server="youtube", url=url , thumbnail=thumbnail , plot=plot , fanart=thumbnail , viewmode="movie_with_plot", folder=False ) )

    current_offset = scrapertools.find_single_match(item.url,"offset=(\d+)")
    if current_offset=="":
        next_page_url = item.url+"&offset=60"
    else:
        new_offset = str(int(current_offset)+60)
        next_page_url = item.url.replace("offset="+current_offset,"offset="+new_offset)
    itemlist.append( Item( channel=item.channel , title=">> Página siguiente" , action="episodios" , url=next_page_url , folder=True ) )

    return itemlist
