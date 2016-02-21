# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Download and play
#------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
#------------------------------------------------------------
# Based on code from the Mega add-on (xbmchub.com)
#---------------------------------------------------------------------------

import os
import sys
import re
import urlparse
import urllib
import urllib2
import locale
import threading
import time
import socket

import xbmc
import xbmcgui

from core import config
from core import logger
from core import downloadtools

# Download a file and start playing while downloading
def download_and_play(url,file_name,download_path,show_dialog=True):
    # Lanza thread
    logger.info("[download_and_play.py] Active threads "+str(threading.active_count()))
    logger.info("[download_and_play.py] "+repr(threading.enumerate()))
    logger.info("[download_and_play.py] Starting download thread...")
    download_thread = DownloadThread(url,file_name,download_path)
    download_thread.start()
    logger.info("[download_and_play.py] Download thread started")
    logger.info("[download_and_play.py] Active threads "+str(threading.active_count()))
    logger.info("[download_and_play.py] "+repr(threading.enumerate()))

    # Espera
    logger.info("[download_and_play.py] Waiting...")

    while True:
        cancelled=False

        if show_dialog:
            dialog = xbmcgui.DialogProgress()
            dialog.create('Descargando...', 'Cierra esta ventana para empezar la reproducción')
            dialog.update(0)

            while not cancelled and download_thread.is_alive():
                dialog.update( download_thread.get_progress() , "Cancela esta ventana para empezar la reproducción", "Velocidad: "+str(int(download_thread.get_speed()/1024))+" KB/s "+str(download_thread.get_actual_size())+"MB de "+str(download_thread.get_total_size())+"MB" , "Tiempo restante: "+str( downloadtools.sec_to_hms(download_thread.get_remaining_time())) )
                xbmc.sleep(1000)

                if dialog.iscanceled():
                    cancelled=True
                    break

            dialog.close()
        else:
            xbmc.executebuiltin((u'XBMC.Notification("Iniciando", "Iniciando descarga en segundo plano...", 300)'))
            xbmc.sleep(3000)

        logger.info("[download_and_play.py] End of waiting")

        # Lanza el reproductor
        player = CustomPlayer()
        player.set_download_thread(download_thread)
        player.PlayStream( download_thread.get_file_name() )

        # Fin de reproducción
        logger.info("[download_and_play.py] Fin de reproducción")

        if player.is_stopped():
            logger.info("[download_and_play.py] Terminado por el usuario")
            break
        else:
            if not download_thread.is_alive():
                logger.info("[download_and_play.py] La descarga ha terminado")
                break
            else:
                logger.info("[download_and_play.py] Continua la descarga")

    # Cuando el reproductor acaba, si continúa descargando lo para ahora
    logger.info("[download_and_play.py] Download thread alive="+str(download_thread.is_alive()))
    if download_thread.is_alive():
        logger.info("[download_and_play.py] Killing download thread")
        download_thread.force_stop()


class CustomPlayer(xbmc.Player):
    def __init__( self, *args, **kwargs ):
        logger.info("CustomPlayer.__init__")
        self.actualtime=0
        self.totaltime=0
        self.stopped=False
        xbmc.Player.__init__( self )

    def PlayStream(self, url):  
        logger.info("CustomPlayer.PlayStream url="+url)
        self.play(url)
        self.actualtime=0
        self.url=url
        while self.isPlaying():
            self.actualtime = self.getTime()
            self.totaltime = self.getTotalTime()
            logger.info("CustomPlayer.PlayStream actualtime="+str(self.actualtime)+" totaltime="+str(self.totaltime))
            xbmc.sleep(3000)

    def set_download_thread(self,download_thread):
        logger.info("CustomPlayer.set_download_thread")
        self.download_thread = download_thread

    def force_stop_download_thread(self):
        logger.info("CustomPlayer.force_stop_download_thread")

        if self.download_thread.is_alive():
            logger.info("CustomPlayer.force_stop_download_thread Killing download thread")
            self.download_thread.force_stop()

            #while self.download_thread.is_alive():
            #    xbmc.sleep(1000)

    def onPlayBackStarted(self):
        logger.info("CustomPlayer.onPlayBackStarted PLAYBACK STARTED")

    def onPlayBackEnded(self):
        logger.info("CustomPlayer.onPlayBackEnded PLAYBACK ENDED")

    def onPlayBackStopped(self):
        logger.info("CustomPlayer.onPlayBackStopped PLAYBACK STOPPED")
        self.stopped=True
        self.force_stop_download_thread()

    def is_stopped(self):
        return self.stopped

# Download in background
class DownloadThread(threading.Thread):
    
    def __init__(self, url, file_name, download_path):
        logger.info("DownloadThread.__init__ "+repr(file))
        self.url = url
        self.download_path = download_path
        self.file_name = os.path.join( download_path , file_name )
        self.progress = 0
        self.force_stop_file_name = os.path.join( self.download_path , "force_stop.tmp" )
        self.velocidad=0
        self.tiempofalta=0
        self.actual_size=0
        self.total_size=0

        if os.path.exists(self.force_stop_file_name):
            os.remove(self.force_stop_file_name)

        threading.Thread.__init__(self)

    def run(self):
        logger.info("DownloadThread.run Download starts...")
        self.download_file()
        logger.info("DownloadThread.run Download ends")

    def force_stop(self):
        logger.info("DownloadThread.force_stop...")
        force_stop_file = open( self.force_stop_file_name , "w" )
        force_stop_file.write("0")
        force_stop_file.close()

    def get_progress(self):
        return self.progress;

    def get_file_name(self):
        return self.file_name

    def get_speed(self):
        return self.velocidad

    def get_remaining_time(self):
        return self.tiempofalta

    def get_actual_size(self):
        return self.actual_size

    def get_total_size(self):
        return self.total_size

    def download_file(self):
        headers=[]

        # Se asegura de que el fichero se podrá crear
        logger.info("DownloadThread.download_file nombrefichero="+self.file_name)
        self.file_name = xbmc.makeLegalFilename(self.file_name)
        logger.info("DownloadThread.download_file nombrefichero="+self.file_name)
        logger.info("DownloadThread.download_file url="+self.url)
    
        # Crea el fichero
        existSize = 0
        f = open(self.file_name, 'wb')
        grabado = 0

        # Login y password Filenium
        # http://abcd%40gmail.com:mipass@filenium.com/get/Oi8vd3d3/LmZpbGVz/ZXJ2ZS5j/b20vZmls/ZS9kTnBL/dm11/b0/?.zip
        if "filenium" in self.url:
            from servers import filenium
            self.url , authorization_header = filenium.extract_authorization_header(self.url)
            headers.append( [ "Authorization", authorization_header ] )

        # Interpreta las cabeceras en una URL como en XBMC
        if "|" in self.url:
            additional_headers = self.url.split("|")[1]
            if "&" in additional_headers:
                additional_headers = additional_headers.split("&")
            else:
                additional_headers = [ additional_headers ]
    
            for additional_header in additional_headers:
                logger.info("DownloadThread.download_file additional_header: "+additional_header)
                name = re.findall( "(.*?)=.*?" , additional_header )[0]
                value = urllib.unquote_plus(re.findall( ".*?=(.*?)$" , additional_header )[0])
                headers.append( [ name,value ] )
    
            self.url = self.url.split("|")[0]
            logger.info("DownloadThread.download_file url="+self.url)
    
        # Timeout del socket a 60 segundos
        socket.setdefaulttimeout(60)

        # Crea la petición y añade las cabeceras
        h=urllib2.HTTPHandler(debuglevel=0)
        request = urllib2.Request(self.url)
        for header in headers:
            logger.info("DownloadThread.download_file Header="+header[0]+": "+header[1])
            request.add_header(header[0],header[1])

        # Lanza la petición
        opener = urllib2.build_opener(h)
        urllib2.install_opener(opener)
        try:
            connexion = opener.open(request)
        except urllib2.HTTPError,e:
            logger.info("DownloadThread.download_file error %d (%s) al abrir la url %s" % (e.code,e.msg,self.url))
            #print e.code
            #print e.msg
            #print e.hdrs
            #print e.fp
            f.close()

            # El error 416 es que el rango pedido es mayor que el fichero => es que ya está completo
            if e.code==416:
                return 0
            else:
                return -2
    
        try:
            totalfichero = int(connexion.headers["Content-Length"])
        except:
            totalfichero = 1

        self.total_size = int(float(totalfichero) / float(1024*1024))
                
        logger.info("Content-Length=%s" % totalfichero)        
        blocksize = 100*1024
    
        bloqueleido = connexion.read(blocksize)
        logger.info("DownloadThread.download_file Iniciando descarga del fichero, bloqueleido=%s" % len(bloqueleido))
    
        maxreintentos = 10

        while len(bloqueleido)>0:
            try:
                if os.path.exists(self.force_stop_file_name):
                    logger.info("DownloadThread.download_file Detectado fichero force_stop, se interrumpe la descarga")
                    f.close()

                    xbmc.executebuiltin((u'XBMC.Notification("Cancelado", "Descarga en segundo plano cancelada", 300)'))

                    return

                # Escribe el bloque leido
                #try:
                #    import xbmcvfs
                #    f.write( bloqueleido )
                #except:
                f.write(bloqueleido)
                grabado = grabado + len(bloqueleido)
                logger.info("DownloadThread.download_file grabado=%d de %d" % (grabado,totalfichero) )
                percent = int(float(grabado)*100/float(totalfichero))
                self.progress=percent;
                totalmb = float(float(totalfichero)/(1024*1024))
                descargadosmb = float(float(grabado)/(1024*1024))
                self.actual_size = int(descargadosmb)
    
                # Lee el siguiente bloque, reintentando para no parar todo al primer timeout
                reintentos = 0
                while reintentos <= maxreintentos:
                    try:

                        before = time.time()
                        bloqueleido = connexion.read(blocksize)
                        after = time.time()
                        if (after - before) > 0:
                            self.velocidad=len(bloqueleido)/((after - before))
                            falta=totalfichero-grabado
                            if self.velocidad>0:
                                self.tiempofalta=falta/self.velocidad
                            else:
                                self.tiempofalta=0
                        break
                    except:
                        reintentos = reintentos + 1
                        logger.info("DownloadThread.download_file ERROR en la descarga del bloque, reintento %d" % reintentos)
                        for line in sys.exc_info():
                            logger.error( "%s" % line )
                
                # Ha habido un error en la descarga
                if reintentos > maxreintentos:
                    logger.info("DownloadThread.download_file ERROR en la descarga del fichero")
                    f.close()
    
                    return -2
    
            except:
                import traceback,sys
                from pprint import pprint
                exc_type, exc_value, exc_tb = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_tb)
                for line in lines:
                    line_splits = line.split("\n")
                    for line_split in line_splits:
                        logger.error(line_split)

                f.close()
                return -2

        return