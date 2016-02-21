# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Logger (kodi)
#------------------------------------------------------------
# tvalacarta
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
# Creado por: Jesús (tvalacarta@gmail.com)
# Licencia: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
#------------------------------------------------------------
# Historial de cambios:
#------------------------------------------------------------

from core import config
loggeractive = (config.get_setting("debug")=="true")

import xbmc

def log_enable(active):
    global loggeractive
    loggeractive = active

def info(texto):
    if loggeractive:
        try:
            xbmc.log(texto)
        except:
            validchars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
            stripped = ''.join(c for c in texto if c in validchars)
            xbmc.log("(stripped) "+stripped)

def debug(texto):
    if loggeractive:
        try:
            xbmc.log(texto)
        except:
            validchars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
            stripped = ''.join(c for c in texto if c in validchars)
            xbmc.log("(stripped) "+stripped)

def error(texto):
    if loggeractive:
        try:
            xbmc.log(texto)
        except:
            validchars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
            stripped = ''.join(c for c in texto if c in validchars)
            xbmc.log("(stripped) "+stripped)
