# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Configuracion
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import os
from types import *

def get_system_platform():
    return ""
    
def open_settings():
    return

def get_platform():
    return "plex"

def get_setting(name,channel=""):

    if name=="cache.dir":
        return ""

    if name=="debug":
        return "false"
    
    if name=="download.enabled":
        return "false"
    
    if name=="cookies.dir":
        return os.getcwd()

    if name=="cache.mode":
        return "2"

    if name=="thumbnail_type":
        return "2"

    else:
        import bridge
        try:
            devuelve = bridge.get_setting(name)
        except:
            devuelve = ""
        
        if type(devuelve) == BooleanType:
            if devuelve:
                devuelve = "true"
            else:
                devuelve = "false"
        
        return devuelve

def set_setting(name,value):
    return ""

def get_localized_string(code):
    import bridge
    return bridge.get_localized_string(code)

def get_library_path():
    return ""

def get_temp_file(filename):
    return ""

def get_runtime_path():
    return os.getcwd()

def get_data_path():
    return os.getcwd()

def get_cookie_data():
    import os
    ficherocookies = os.path.join( get_data_path(), 'cookies.lwp' )

    cookiedatafile = open(ficherocookies,'r')
    cookiedata = cookiedatafile.read()
    cookiedatafile.close();

    return cookiedata
