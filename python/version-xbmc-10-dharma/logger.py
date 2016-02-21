# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Módulo de logging - xbmc dharma
#------------------------------------------------------------
# pelisalacarta
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
# Creado por: Jesús (tvalacarta@gmail.com)
# Licencia: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
#------------------------------------------------------------
# Historial de cambios:
#------------------------------------------------------------

import xbmc

def info(texto):
    try:
        xbmc.output(texto)
    except:
        validchars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
        stripped = ''.join(c for c in texto if c in validchars)
        xbmc.output("(stripped) "+stripped)

def debug(texto):
    try:
        xbmc.output(texto)
    except:
        validchars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
        stripped = ''.join(c for c in texto if c in validchars)
        xbmc.output("(stripped) "+stripped)

def error(texto):
    try:
        xbmc.output(texto)
    except:
        validchars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
        stripped = ''.join(c for c in texto if c in validchars)
        xbmc.output("(stripped) "+stripped)
