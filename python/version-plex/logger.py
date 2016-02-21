# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Logger
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import bridge

def info(texto):
    try:
        bridge.log_info( texto )
    except:
        pass
    
def debug(texto):
    try:
        bridge.log_info( texto )
    except:
        pass

def error(texto):
    try:
        bridge.log_info( texto )
    except:
        pass
